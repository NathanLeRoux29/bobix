from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas.task import TaskCreate, TaskRead, TaskUpdate
from app.services import tasks as tasks_service

router = APIRouter()


@router.get("/", response_model=list[TaskRead])
def list_tasks(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Return a paginated list of all tasks."""
    return tasks_service.get_tasks(db, skip=skip, limit=limit)


@router.get("/focus", response_model=list[TaskRead])
def focus_tasks(db: Session = Depends(get_db)):
    """Return tasks marked as focus that are not yet completed (used by the Hub widget)."""
    return tasks_service.get_focus_tasks(db)


@router.get("/{task_id}", response_model=TaskRead)
def get_task(task_id: int, db: Session = Depends(get_db)):
    """Return a single task by ID. Raises 404 if not found."""
    task = tasks_service.get_task(db, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@router.post("/", response_model=TaskRead, status_code=201)
def create_task(task: TaskCreate, db: Session = Depends(get_db)):
    """Create a new task and return it."""
    return tasks_service.create_task(db, task)


@router.patch("/{task_id}", response_model=TaskRead)
def update_task(task_id: int, task: TaskUpdate, db: Session = Depends(get_db)):
    """Partially update a task. Raises 404 if not found."""
    updated = tasks_service.update_task(db, task_id, task)
    if not updated:
        raise HTTPException(status_code=404, detail="Task not found")
    return updated


@router.delete("/{task_id}", status_code=204)
def delete_task(task_id: int, db: Session = Depends(get_db)):
    """Delete a task by ID. Raises 404 if not found."""
    if not tasks_service.delete_task(db, task_id):
        raise HTTPException(status_code=404, detail="Task not found")
