# FastAPI + Celery Image Processing API

## Overview
This project provides an **asynchronous image processing API** using **FastAPI, Celery, and Redis**.  
It accepts a **CSV file with image URLs**, compresses the images, stores the results in a database, and provides endpoints to check the status and retrieve results as a downloadable CSV.

---

## Tech Stack
- **FastAPI** - Web framework for the API  
- **Celery** - Task queue for async processing  
- **Redis** - Message broker for Celery  
- **SQLite** - Database to store processed data  
- **Pillow** - Image processing library  

---

## Features
✅ **Upload CSV** - Accepts a CSV file with image URLs and processes images asynchronously  
✅ **Asynchronous Processing** - Uses Celery to compress images in the background  
✅ **Check Task Status** - Get the status of a task by ID  
✅ **Retrieve Processed CSV** - Download a CSV containing original & compressed image URLs  
✅ **Serve Compressed Images** - View/download compressed images via an endpoint  
✅ **Webhook Support** - Notifies a webhook URL when processing is complete  

---

## Installation

### 1️⃣ Clone the Repository
```sh
git clone https://github.com/singhal-abhi/Image-Resizer.git
cd Image-Resizer
```

### 2️⃣ Create a Virtual Environment
```sh
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3️⃣ Install Dependencies
```sh
pip install -r requirements.txt
```

### 4️⃣ Start Redis (If Not Running)
- **Using Docker**  
  ```sh
  docker run -d --name redis -p 6379:6379 redis
  ```
- **On Linux/macOS**  
  ```sh
  sudo systemctl start redis
  ```

---

## Usage

### 1️⃣ Start FastAPI Server
```sh
uvicorn main:app --port=8000
```

### 2️⃣ Start Celery Worker
```sh
celery -A celery_config.celery_worker worker --loglevel=info
```
### 3️⃣ Start Webhook Receiver(Optional)
```sh
uvicorn webhook_receiver:app --port=8002
```

---

## API Endpoints

### 1️⃣ Upload CSV
**Endpoint:**
```http
POST /upload
```
**Description:** Uploads a CSV file and starts processing.  
**Request Parameters:**  
- `file`: CSV file with columns **Serial Number, Product Name, Input Image Urls**  
**Response Example:**
```json
{ "task_id": "123e4567-e89b-12d3-a456-426614174000" }
```

### 2️⃣ Check Task Status
**Endpoint:**
```http
GET /status/{task_id}
```
**Description:** Check the status of a processing task.  
**Response Example:**
```json
{ "task_id": "123e4567-e89b-12d3-a456-426614174000", "status": "PENDING" }
```

### 3️⃣ Retrieve Processed CSV
**Endpoint:**
```http
GET /result/{task_id}
```
**Description:** Download a CSV containing original and compressed image URLs.  
**Response:** A CSV file.

### 4️⃣ Serve Compressed Images
**Endpoint:**
```http
GET /compressed/{filename}
```
**Description:** Fetch a compressed image.  
**Response:** The compressed image file.

### 5️⃣ Ping API
**Endpoint:**
```http
GET /ping
```
**Description:** Check if the server is running.  
**Response Example:**
```json
{ "status": "pong" }
```

---

## Example Input CSV
```csv
Serial Number,Product Name,Input Image Urls
1,SKU1,https://picsum.photos/200/300,https://picsum.photos/250/350
2,SKU2,https://placekitten.com/200/300,https://placekitten.com/250/350
```

---

## Webhook
When the image processing task completes, it **triggers a webhook**:
**Endpoint:**
```http
POST http://127.0.0.1:8002/webhook
```
**Payload Example:**
```json
{
    "SKU1": {
        "input_urls": ["https://picsum.photos/200/300", "https://picsum.photos/250/350"],
        "output_urls": ["http://127.0.0.1:8000/compressed/compressed_SKU1_1.jpg", "http://127.0.0.1:8000/compressed/compressed_SKU1_2.jpg"]
    }
}
```

---

## Troubleshooting

### Redis Not Running
If Celery fails to connect to Redis, start Redis:
```sh
redis-server
```
or use Docker:
```sh
docker start redis
```

### Celery Task Not Found
Make sure Celery is started with:
```sh
celery -A celery_config.celery_worker worker --loglevel=info
```

---

## License
This project is licensed under the MIT License.
