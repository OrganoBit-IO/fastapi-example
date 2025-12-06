import asyncio
import uuid
from datetime import datetime
from typing import Optional, Union

from fastapi import BackgroundTasks, FastAPI, HTTPException, status
from fastapi.responses import StreamingResponse

from app.models import (
    BatchProcessRequest,
    EchoRequest,
    ProcessJobCreate,
    Task,
    TaskCreate,
    TaskUpdate,
)
from app.storage import job_storage, task_storage

app = FastAPI(
    title="FastAPI Example API",
    description="Example API demonstrating CRUD operations, background tasks, and async patterns",
    version="1.0.0",
)


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/items/{item_id}")
def read_item(item_id: int, q: Union[str, None] = None):
    return {"item_id": item_id, "q": q}


@app.post("/tasks", response_model=Task, status_code=status.HTTP_201_CREATED)
def create_task(task_data: TaskCreate):
    task = task_storage.create(
        title=task_data.title,
        description=task_data.description,
        status=task_data.status
    )
    return task


@app.get("/tasks", response_model=list[Task])
def list_tasks(status_filter: Optional[str] = None):
    if status_filter and status_filter not in ["pending", "in_progress", "completed"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid status filter. Must be: pending, in_progress, or completed"
        )
    return task_storage.get_all(status=status_filter)


@app.get("/tasks/{task_id}", response_model=Task)
def get_task(task_id: int):
    task = task_storage.get(task_id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task with id {task_id} not found"
        )
    return task


@app.put("/tasks/{task_id}", response_model=Task)
def update_task(task_id: int, task_data: TaskUpdate):
    task = task_storage.update(
        task_id=task_id,
        title=task_data.title,
        description=task_data.description,
        status=task_data.status
    )
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task with id {task_id} not found"
        )
    return task


@app.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(task_id: int):
    deleted = task_storage.delete(task_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task with id {task_id} not found"
        )


def send_notification(task_id: int, task_title: str):
    import time
    time.sleep(2)
    print(f"NOTIFICATION SENT: Task '{task_title}' (ID: {task_id}) has been created")


@app.post("/tasks/{task_id}/notify")
def notify_task_creation(task_id: int, background_tasks: BackgroundTasks):
    task = task_storage.get(task_id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task with id {task_id} not found"
        )

    background_tasks.add_task(send_notification, task_id, task.title)
    return {"message": f"Notification queued for task {task_id}"}


def process_job_background(job_id: str, data: list[str], delay: float):
    import time
    job_storage.update_status(job_id, "processing")
    time.sleep(delay)
    result = f"Processed {len(data)} items: {', '.join(data)}"
    job_storage.update_status(job_id, "completed", result)
    print(f"JOB COMPLETED: {job_id} - {result}")


@app.post("/process", status_code=status.HTTP_202_ACCEPTED)
def start_background_job(job_data: ProcessJobCreate, background_tasks: BackgroundTasks):
    job_id = f"job-{uuid.uuid4().hex[:8]}"
    job = job_storage.create(job_id, job_data.data)

    background_tasks.add_task(process_job_background, job_id, job_data.data, job_data.delay)

    return {
        "message": "Job queued for processing",
        "job_id": job_id,
        "status_url": f"/jobs/{job_id}"
    }


@app.get("/jobs/{job_id}")
def get_job_status(job_id: str):
    job = job_storage.get(job_id)
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Job with id {job_id} not found"
        )
    return job


@app.get("/async/external")
async def simulate_external_api():
    await asyncio.sleep(2)
    return {
        "message": "Simulated external API response",
        "timestamp": datetime.now().isoformat(),
        "data": {"result": "success", "value": 42}
    }


@app.post("/async/batch")
async def process_batch(batch: BatchProcessRequest):
    async def process_item(item: str, delay: float) -> dict[str, str]:
        await asyncio.sleep(delay)
        return {
            "item": item,
            "processed_at": datetime.now().isoformat(),
            "status": "completed"
        }

    tasks = [process_item(item, batch.delay) for item in batch.items]
    results = await asyncio.gather(*tasks)

    return {
        "message": f"Processed {len(batch.items)} items concurrently",
        "results": results
    }


async def event_generator():
    for i in range(5):
        await asyncio.sleep(1)
        yield f"data: Event {i + 1} at {datetime.now().isoformat()}\n\n"


@app.get("/async/stream")
async def stream_events():
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream"
    )


@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "fastapi-example",
        "version": "1.0.0"
    }


@app.post("/echo")
def echo_request(request: EchoRequest):
    return {
        "received": request.message,
        "metadata": request.metadata,
        "timestamp": datetime.now().isoformat(),
        "echo": request.message
    }


@app.get("/error")
def trigger_error(code: int = 500):
    error_messages = {
        400: "Bad Request - Invalid input",
        401: "Unauthorized - Authentication required",
        403: "Forbidden - Access denied",
        404: "Not Found - Resource does not exist",
        500: "Internal Server Error - Something went wrong",
        503: "Service Unavailable - Service is temporarily unavailable"
    }

    if code not in error_messages:
        code = 500

    raise HTTPException(
        status_code=code,
        detail=error_messages[code]
    )