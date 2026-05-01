from datetime import datetime
from pydantic import BaseModel


class NoteBase(BaseModel):
    title: str
    content: str = ""
    folder_id: int | None = None
    is_favorite: bool = False


class NoteCreate(NoteBase):
    pass


class NoteUpdate(BaseModel):
    title: str | None = None
    content: str | None = None
    folder_id: int | None = None
    is_favorite: bool | None = None


class NoteRead(NoteBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}