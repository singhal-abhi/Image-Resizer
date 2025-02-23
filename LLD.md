# Low-Level Design (LLD) Document

## Overview

This document provides a detailed technical design of the Image Resizer project. The project is built using FastAPI, Celery, Redis, and SQLite. It processes CSV files containing image URLs, compresses the images, stores the results in a database, and provides endpoints to check the status and retrieve results as a downloadable CSV. Additionally, it includes a webhook receiver to handle updates.

## Components

1. **FastAPI Application**
2. **Celery Worker**
3. **Redis**
4. **SQLite Database**
5. **Webhook Receiver**

## Visual Diagram

You can create a visual diagram using Draw.io or any similar tool. Below is a textual representation of the system components and their interactions:

```
+-------------------+       +-------------------+       +-------------------+
|                   |       |                   |       |                   |
|   FastAPI Server  | <---> |   Celery Worker   | <---> |  Webhook Receiver |
|                   |       |                   |       |                   |
+-------------------+       +-------------------+       +-------------------+
        |                           |                          
        |                           |                           
        v                           v                           
+-------------------+       +-------------------+       
|                   |       |     Process       |
|   SQLite Database |       |    Image URLs     |        
|                   |       |                   |  
+-------------------+       +-------------------+       
```

## Component Descriptions

### 1. FastAPI Application

- **Role:** Acts as the main entry point for the API. Handles incoming requests, such as uploading CSV files, checking task status, retrieving results, and serving compressed images.
- **Functions:**
  - `/upload`: Handles the upload of a CSV file and processes it asynchronously.
  - `/status/{task_id}`: Checks the status of a Celery task by task ID.
  - `/result/{task_id}`: Retrieves the result of a processed CSV task as a downloadable CSV file.
  - `/compressed/{filename}`: Retrieves a compressed image by filename.
  - `/ping`: Endpoint to check if the server is running.

### 2. Celery Worker

- **Role:** Processes tasks asynchronously. Compresses images and stores the results in the database.
- **Functions:**
  - `process_csv`: Processes a CSV string containing image URLs, compresses the images, and stores the results in the database.
  - `compress_image`: Compresses an image from the given URL and saves it to the upload folder.

### 3. Redis

- **Role:** Acts as a message broker for Celery. Manages task queues and facilitates communication between the FastAPI server and Celery worker.
- **Functions:**
  - Stores task states and results.
  - Manages task queues.

### 4. SQLite Database

- **Role:** Stores the results of the image processing tasks.
- **Functions:**
  - Stores processed image data, including input URLs and output URLs.
  - Provides data retrieval for the FastAPI server.

### 5. Webhook Receiver

- **Role:** Receives updates from the webhook when image processing is complete.
- **Functions:**
  - `/webhook`: Receives updates from the webhook.
  - `/ping`: Endpoint to check if the server is running.

## Detailed Technical Design

### 1. FastAPI Application

- **File:** `main.py`
- **Endpoints:**
  - `/upload`: Accepts a CSV file and starts processing.
  - `/status/{task_id}`: Returns the status of a task.
  - `/result/{task_id}`: Returns the processed CSV result.
  - `/compressed/{filename}`: Returns the compressed image.
  - `/ping`: Returns a "pong" response to check if the server is running.

### 2. Celery Worker

- **File:** `celery_config.py`
- **Tasks:**
  - `process_csv`: Processes the CSV file, compresses images, and stores results.
  - `compress_image`: Compresses an image and saves it to the upload folder.

### 3. Redis

- **Configuration:** Redis server running on `localhost:6379`.
- **Usage:** Used by Celery for task management and communication.

### 4. SQLite Database

- **File:** `database.py`
- **Tables:**
  - `ImageProcessing`: Stores processed image data, including input URLs and output URLs.

### 5. Webhook Receiver

- **File:** `webhook_receiver.py`
- **Endpoints:**
  - `/webhook`: Receives updates from the webhook.
  - `/ping`: Returns a "pong" response to check if the server is running.


This detailed technical design document provides an overview of the system components, their roles, and functions. It also includes a visual representation of the system architecture.