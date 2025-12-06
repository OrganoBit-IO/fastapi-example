from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class TaskCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200, description="Task title")
    description: Optional[str] = Field(None, max_length=1000, description="Task description")
    status: str = Field(default="pending", pattern="^(pending|in_progress|completed)$")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "title": "Complete project documentation",
                    "description": "Write comprehensive API documentation",
                    "status": "pending"
                }
            ]
        }
    }


class TaskUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    status: Optional[str] = Field(None, pattern="^(pending|in_progress|completed)$")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "status": "completed"
                }
            ]
        }
    }


class Task(BaseModel):
    id: int
    title: str
    description: Optional[str]
    status: str
    created_at: datetime
    updated_at: datetime

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "id": 1,
                    "title": "Complete project documentation",
                    "description": "Write comprehensive API documentation",
                    "status": "pending",
                    "created_at": "2025-12-06T10:00:00",
                    "updated_at": "2025-12-06T10:00:00"
                }
            ]
        }
    }


class ProcessJobCreate(BaseModel):
    data: list[str] = Field(..., min_length=1, description="Items to process")
    delay: float = Field(default=2.0, ge=0.1, le=10.0, description="Simulated processing delay in seconds")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "data": ["item1", "item2", "item3"],
                    "delay": 2.0
                }
            ]
        }
    }


class ProcessJob(BaseModel):
    id: str
    status: str
    data: list[str]
    result: Optional[str]
    created_at: datetime
    completed_at: Optional[datetime]

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "id": "job-123",
                    "status": "processing",
                    "data": ["item1", "item2"],
                    "result": None,
                    "created_at": "2025-12-06T10:00:00",
                    "completed_at": None
                }
            ]
        }
    }


class EchoRequest(BaseModel):
    message: str
    metadata: Optional[dict[str, str]] = None

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "message": "Hello, FastAPI!",
                    "metadata": {"user": "test", "environment": "dev"}
                }
            ]
        }
    }


class BatchProcessRequest(BaseModel):
    items: list[str] = Field(..., min_length=1, max_length=10)
    delay: float = Field(default=1.0, ge=0.1, le=5.0, description="Delay per item in seconds")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "items": ["task1", "task2", "task3"],
                    "delay": 1.0
                }
            ]
        }
    }
