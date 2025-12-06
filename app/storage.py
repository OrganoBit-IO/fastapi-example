from datetime import datetime
from typing import Optional
from app.models import Task, ProcessJob


class TaskStorage:
    def __init__(self):
        self.tasks: dict[int, Task] = {}
        self.next_id: int = 1

    def create(self, title: str, description: Optional[str], status: str) -> Task:
        now = datetime.now()
        task = Task(
            id=self.next_id,
            title=title,
            description=description,
            status=status,
            created_at=now,
            updated_at=now
        )
        self.tasks[self.next_id] = task
        self.next_id += 1
        return task

    def get(self, task_id: int) -> Optional[Task]:
        return self.tasks.get(task_id)

    def get_all(self, status: Optional[str] = None) -> list[Task]:
        if status:
            return [task for task in self.tasks.values() if task.status == status]
        return list(self.tasks.values())

    def update(self, task_id: int, title: Optional[str] = None,
               description: Optional[str] = None, status: Optional[str] = None) -> Optional[Task]:
        task = self.tasks.get(task_id)
        if not task:
            return None

        if title is not None:
            task.title = title
        if description is not None:
            task.description = description
        if status is not None:
            task.status = status

        task.updated_at = datetime.now()
        return task

    def delete(self, task_id: int) -> bool:
        if task_id in self.tasks:
            del self.tasks[task_id]
            return True
        return False


class JobStorage:
    def __init__(self):
        self.jobs: dict[str, ProcessJob] = {}

    def create(self, job_id: str, data: list[str]) -> ProcessJob:
        job = ProcessJob(
            id=job_id,
            status="queued",
            data=data,
            result=None,
            created_at=datetime.now(),
            completed_at=None
        )
        self.jobs[job_id] = job
        return job

    def get(self, job_id: str) -> Optional[ProcessJob]:
        return self.jobs.get(job_id)

    def update_status(self, job_id: str, status: str, result: Optional[str] = None) -> Optional[ProcessJob]:
        job = self.jobs.get(job_id)
        if not job:
            return None

        job.status = status
        if result is not None:
            job.result = result
        if status == "completed":
            job.completed_at = datetime.now()

        return job


task_storage = TaskStorage()
job_storage = JobStorage()
