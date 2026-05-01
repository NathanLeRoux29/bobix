from datetime import datetime
from pydantic import BaseModel


class FolderBase(BaseModel):
    name: str
    parent_id: int | None = None


class FolderCreate(FolderBase):
    pass


class FolderUpdate(BaseModel):
    name: str | None = None
    parent_id: int | None = None


class FolderRead(FolderBase):
    id: int
    created_at: datetime

    model_config = {"from_attributes": True}