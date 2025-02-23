from fastapi import FastAPI, Request
import logging

app = FastAPI()


@app.post("/webhook")
async def receive_webhook(request: Request):
    """
    Receives updates from the webhook.

    Args:
        request (Request): The request object containing the webhook payload.

    Returns:
        dict: A dictionary containing the status of the received webhook.
    """
    try:
        payload = await request.json()
        print(f"Webhook received: {payload}")
        # Process the payload as needed
        return {"status": "success"}
    except Exception as e:
        logging.error(f"Error receiving webhook: {e}")
        return {"status": "error", "message": str(e)}


@app.get("/ping")
def ping():
    """
    Endpoint to check if the server is running.

    Returns:
        dict: A dictionary containing a "status" key with the value "pong".
    """
    return {"status": "pong"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)
