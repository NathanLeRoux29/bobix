from datetime import datetime, timezone
from sqlalchemy.orm import Session
from app.models.task import Task
from app.schemas.task import TaskCreate, TaskUpdate


def get_tasks(db: Session, skip: int = 0, limit: int = 100) -> list[Task]:
    """Return a paginated list of all tasks."""
    return db.query(Task).offset(skip).limit(limit).all()


def get_task(db: Session, task_id: int) -> Task | None:
    """Return a single task by ID, or None if not found."""
    return db.query(Task).filter(Task.id == task_id).first()


def get_focus_tasks(db: Session) -> list[Task]:
    """Return tasks marked as focus that are not yet completed."""
    return db.query(Task).filter(Task.is_focus.is_(True), Task.is_completed.is_(False)).all()


def create_task(db: Session, task: TaskCreate) -> Task:
    """Insert a new task and return it with its generated ID."""
    db_task = Task(**task.model_dump())
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task


def update_task(db: Session, task_id: int, task: TaskUpdate) -> Task | None:
    """Apply partial updates to a task. Returns None if task not found."""
    db_task = get_task(db, task_id)
    if not db_task:
        return None
    for field, value in task.model_dump(exclude_unset=True).items():
        setattr(db_task, field, value)
    db_task.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(db_task)
    return db_task


def delete_task(db: Session, task_id: int) -> bool:
    """Delete a task by ID. Returns False if task not found."""
    db_task = get_task(db, task_id)
    if not db_task:
        return False
    db.delete(db_task)
    db.commit()
    return True
