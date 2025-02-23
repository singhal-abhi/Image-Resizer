import csv
import io
import json
import logging
import os
from pathlib import Path
from fastapi.responses import FileResponse
from fastapi import FastAPI, Request, Response, UploadFile, File
from celery_config import celery_worker
import requests
from PIL import Image
from io import BytesIO
import redis
from database import ImageProcessing, SessionLocal
import aiohttp
import asyncio

UPLOAD_FOLDER = "compressed_images"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app = FastAPI()

# Configure Redis
redis_client = redis.Redis(host='localhost', port=6379,
                           db=0, decode_responses=True)


@app.post("/upload")
def upload_csv(request: Request, file: UploadFile = File(...)):
    """
    Handles the upload of a CSV file and processes it asynchronously.

    Args:
        request (Request): The request object containing metadata about the request.
        file (UploadFile, optional): The uploaded CSV file. Defaults to File(...).

    Returns:
        dict: A dictionary containing the task ID if the upload is successful,
              or an error message if the upload fails.

    Raises:
        Exception: If there is an error reading or processing the CSV file.
    """
    try:
        csv_data = file.file.read().decode('utf-8')
        print("CSV Received")
        task = process_csv.apply_async(args=[csv_data, str(request.base_url)])
        return {"task_id": task.id}
    except Exception as e:
        logging.error(f"Error uploading CSV: {e}")
        return {"error": "Failed to upload CSV"}


async def trigger_webhook(webhook_url: str, payload: dict):
    """
    Sends a POST request to the specified webhook URL with the given payload.

    Args:
        webhook_url (str): The URL of the webhook to trigger.
        payload (dict): The data to send in the POST request.

    Returns:
        bool: True if the request was successful, False otherwise.
    """
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(webhook_url, json=payload) as response:
                response.raise_for_status()
                return True
    except aiohttp.ClientError as e:
        logging.error(f"Error triggering webhook: {e}")
        return False


@celery_worker.task
def process_csv(csv_data: str, base_url: str):
    """
    Processes a CSV string containing image URLs, compresses the images, and stores the results in a database.

    Args:
        csv_data (str): The CSV data as a string. The CSV should have columns 'Serial Number', 'Product Name', and 'Input Image Urls'.
        base_url (str): The base URL to be used for the compressed images.

    Returns:
        dict: A dictionary containing the results of the image processing. The keys are product names, and the values are dictionaries with 'input_urls' and 'output_urls'.
              If an error occurs, returns a dictionary with an "error" key and a message.

    Raises:
        ValueError: If the CSV data is empty or has an invalid format.
        Exception: If any other error occurs during processing.

    Notes:
        - The function expects the CSV data to have a header row with the columns 'Serial Number', 'Product Name', and 'Input Image Urls'.
        - The function uses a database session to store the results of the image processing.
        - If an error occurs, the function logs the error and stores the error message in the database.
    """
    try:
        lines = csv_data.strip().split("\n")
        db = SessionLocal()

        if not lines:
            raise ValueError("CSV data is empty")

        reader = csv.reader(lines)
        header = next(reader, None)
        if header != ['Serial Number', 'Product Name', 'Input Image Urls']:
            raise ValueError("Invalid CSV format: missing required columns")
        results = {}

        for row in reader:
            if len(row) < 3:
                continue

            serial_number, product_name, *input_urls = row
            output_urls = []

            for url in input_urls:
                compressed_url = compress_image(
                    product_name, url.strip(), base_url)
                output_urls.append(compressed_url)

            results[product_name] = {
                "input_urls": input_urls,
                "output_urls": output_urls
            }
        entry = ImageProcessing(id=process_csv.request.id, data=json.dumps(results),
                                status='Completed')
        db.add(entry)
        db.commit()
        try:
            webhook_url = "http://127.0.0.1:8002/webhook"
            asyncio.run(trigger_webhook(webhook_url, results))
        except Exception as e:
            print(f"Error triggering webhook: {e}")
        return results
    except Exception as e:
        logging.error(f"Error processing CSV: {e}")
        entry = ImageProcessing(id=process_csv.request.id, serial_number=serial_number, data=json.dumps({"error": str(e)}),
                                status='Failed')
        db.add(entry)
        db.commit()
        return {"error": "Failed to process CSV"}


def compress_image(product_name: str, url: str, base_url: str) -> str:
    """
    Compresses an image from the given URL and saves it to the upload folder.

    Args:
        product_name (str): The name of the product associated with the image.
        url (str): The URL of the image to compress.
        base_url (str): The base URL to be used for the compressed images.

    Returns:
        str: The URL of the compressed image if successful, otherwise "File Not Accessible".
    """
    response = requests.get(url)
    if response.status_code == 200:
        img = Image.open(BytesIO(response.content))
        output_path = os.path.join(
            UPLOAD_FOLDER, f"compressed_{product_name}_{Path(url).stem}.jpg")

        img.save(output_path, format='JPEG', quality=50)

        return f"{str(base_url)}compressed/{Path(output_path).name}"
    return "File Not Accessible"


@app.get("/compressed/{filename}")
def get_compressed_image(filename: str):
    """
    Retrieves a compressed image by filename.

    Args:
        filename (str): The name of the compressed image file.

    Returns:
        FileResponse: The compressed image file if found, otherwise an error message.
    """
    file_path = os.path.join(UPLOAD_FOLDER, filename)
    if os.path.exists(file_path):
        return FileResponse(file_path)
    return {"error": "File not found"}


@app.get("/status/{task_id}")
def check_status(task_id: str):
    """
    Checks the status of a Celery task by task ID.

    Args:
        task_id (str): The ID of the Celery task.

    Returns:
        dict: A dictionary containing the task ID, status, and result if the task is successful.
    """
    task_result = celery_worker.AsyncResult(task_id)
    if task_result.state == 'SUCCESS':
        return {"task_id": task_id, "status": task_result.state, "data": task_result.result}
    return {"task_id": task_id, "status": task_result.state}


@app.get("/result/{task_id}")
def get_csv_result(task_id: str):
    """
    Retrieves the result of a processed CSV task as a downloadable CSV file.

    Args:
        task_id (str): The ID of the processed CSV task.

    Returns:
        Response: A CSV file containing the results of the image processing if found, otherwise an error message.
    """
    db = SessionLocal()
    entry = db.query(ImageProcessing).get(task_id)
    if entry:
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(["Serial Number",
                        "Product Name", "Input Urls", "Output Urls"])
        data = json.loads(entry.data)
        for idx, (product_name, value) in enumerate(data.items(), start=1):
            serial_number = value.get("serial_number", idx)
            writer.writerow([serial_number, product_name,
                            *value["input_urls"], *value["output_urls"]])
        response = Response(output.getvalue(), media_type="text/csv")
        response.headers["Content-Disposition"] = f"attachment; filename=result_{task_id}.csv"
        return response
    return {"task_id": task_id, "status": "Not Found"}


@app.get("/ping")
@app.get("/")
def ping():
    """
    Endpoint to check if the server is running.

    Returns:
        dict: A dictionary containing a "status" key with the value "pong".
    """
    return {"status": "pong"}
