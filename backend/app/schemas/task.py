from datetime import datetime, date
from pydantic import BaseModel


class TaskBase(BaseModel):
    title: str
    description: str | None = None
    due_date: date | None = None
    tag: str | None = None
    is_focus: bool = False
    is_completed: bool = False


class TaskCreate(TaskBase):
    pass


class TaskUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    due_date: date | None = None
    tag: str | None = None
    is_focus: bool | None = None
    is_completed: bool | None = None


class TaskRead(TaskBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}