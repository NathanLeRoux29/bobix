# Backend Foundation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the complete FastAPI + PostgreSQL backend with CRUD endpoints for notes, folders, tasks, and settings.

**Architecture:** FastAPI app organized in layers: models (SQLAlchemy), schemas (Pydantic), services (business logic), and API routers. SQLite used for unit tests to avoid requiring Docker in CI; PostgreSQL for dev/prod via Docker Compose.

**Tech Stack:** Python 3.11, FastAPI 0.111, SQLAlchemy 2.0, Pydantic 2, pytest, Docker Compose, PostgreSQL 15.

---

## File Map

**Create:**
- `backend/requirements.txt`
- `backend/Dockerfile`
- `backend/.env.example`
- `docker-compose.yml`
- `docker-compose.prod.yml`
- `backend/app/__init__.py`
- `backend/app/main.py`
- `backend/app/core/__init__.py`
- `backend/app/core/config.py`
- `backend/app/core/database.py`
- `backend/app/models/__init__.py`
- `backend/app/models/folder.py`
- `backend/app/models/note.py`
- `backend/app/models/task.py`
- `backend/app/models/setting.py`
- `backend/app/schemas/__init__.py`
- `backend/app/schemas/folder.py`
- `backend/app/schemas/note.py`
- `backend/app/schemas/task.py`
- `backend/app/schemas/setting.py`
- `backend/app/services/__init__.py`
- `backend/app/services/folders.py`
- `backend/app/services/notes.py`
- `backend/app/services/tasks.py`
- `backend/app/services/settings.py`
- `backend/app/api/__init__.py`
- `backend/app/api/folders.py`
- `backend/app/api/notes.py`
- `backend/app/api/tasks.py`
- `backend/app/api/settings.py`
- `backend/tests/__init__.py`
- `backend/tests/conftest.py`
- `backend/tests/unit/__init__.py`
- `backend/tests/unit/test_notes.py`
- `backend/tests/unit/test_tasks.py`
- `backend/tests/unit/test_settings.py`
- `backend/tests/unit/test_folders.py`
- `backend/tests/integration/__init__.py`
- `backend/tests/integration/test_api.py`

---

## Task 1: Project scaffolding (Docker, deps, env)

**Files:**
- Create: `backend/requirements.txt`
- Create: `backend/Dockerfile`
- Create: `backend/.env.example`
- Create: `docker-compose.yml`
- Create: `docker-compose.prod.yml`

- [ ] **Step 1: Create `backend/requirements.txt`**

```
fastapi==0.111.0
uvicorn[standard]==0.29.0
sqlalchemy==2.0.30
psycopg2-binary==2.9.9
pydantic-settings==2.2.1
httpx==0.27.0
pytest==8.2.0
pytest-asyncio==0.23.6
```

- [ ] **Step 2: Create `backend/Dockerfile`**

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

- [ ] **Step 3: Create `backend/.env.example`**

```
DATABASE_URL=postgresql://dev:dev_password@localhost:5432/myapp_dev
```

- [ ] **Step 4: Create `docker-compose.yml`**

```yaml
services:
  postgres:
    image: postgres:15-alpine
    environment:
      POSTGRES_DB: myapp_dev
      POSTGRES_USER: dev
      POSTGRES_PASSWORD: dev_password
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

  backend:
    build: ./backend
    environment:
      DATABASE_URL: postgresql://dev:dev_password@postgres:5432/myapp_dev
    ports:
      - "8000:8000"
    volumes:
      - ./backend:/app
    depends_on:
      - postgres

volumes:
  postgres_data:
```

- [ ] **Step 5: Create `docker-compose.prod.yml`**

```yaml
services:
  postgres:
    image: postgres:15-alpine
    environment:
      POSTGRES_DB: myapp
      POSTGRES_USER: ${POSTGRES_USER}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    restart: unless-stopped

  backend:
    build: ./backend
    environment:
      DATABASE_URL: postgresql://${POSTGRES_USER}:${POSTGRES_PASSWORD}@postgres:5432/myapp
      CORS_ORIGINS: ${CORS_ORIGINS}
    ports:
      - "8000:8000"
    restart: unless-stopped
    depends_on:
      - postgres

volumes:
  postgres_data:
```

- [ ] **Step 6: Commit**

```bash
git add backend/requirements.txt backend/Dockerfile backend/.env.example docker-compose.yml docker-compose.prod.yml
git commit -m "chore: add backend scaffolding and docker setup"
```

---

## Task 2: Core config and database session

**Files:**
- Create: `backend/app/__init__.py` (empty)
- Create: `backend/app/core/__init__.py` (empty)
- Create: `backend/app/core/config.py`
- Create: `backend/app/core/database.py`

- [ ] **Step 1: Create empty init files**

```bash
touch backend/app/__init__.py backend/app/core/__init__.py
```

- [ ] **Step 2: Create `backend/app/core/config.py`**

```python
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql://dev:dev_password@localhost:5432/myapp_dev"

    class Config:
        env_file = ".env"


settings = Settings()
```

- [ ] **Step 3: Create `backend/app/core/database.py`**

```python
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from app.core.config import settings


engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

- [ ] **Step 4: Commit**

```bash
git add backend/app/
git commit -m "feat: add FastAPI core config and database session"
```

---

## Task 3: SQLAlchemy models

**Files:**
- Create: `backend/app/models/__init__.py`
- Create: `backend/app/models/folder.py`
- Create: `backend/app/models/note.py`
- Create: `backend/app/models/task.py`
- Create: `backend/app/models/setting.py`

- [ ] **Step 1: Create `backend/app/models/folder.py`**

```python
from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base


class Folder(Base):
    __tablename__ = "folders"

    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    parent_id = Column(Integer, ForeignKey("folders.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    parent = relationship("Folder", remote_side=[id], back_populates="children")
    children = relationship("Folder", back_populates="parent")
    notes = relationship("Note", back_populates="folder")
```

- [ ] **Step 2: Create `backend/app/models/note.py`**

```python
from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from app.core.database import Base


class Note(Base):
    __tablename__ = "notes"

    id = Column(Integer, primary_key=True)
    title = Column(String(255), nullable=False)
    content = Column(Text, nullable=False, default="")
    folder_id = Column(Integer, ForeignKey("folders.id"), nullable=True)
    is_favorite = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    folder = relationship("Folder", back_populates="notes")
```

- [ ] **Step 3: Create `backend/app/models/task.py`**

```python
from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Date, Text
from app.core.database import Base


class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    due_date = Column(Date, nullable=True)
    tag = Column(String(100), nullable=True)
    is_focus = Column(Boolean, default=False, nullable=False)
    is_completed = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )
```

- [ ] **Step 4: Create `backend/app/models/setting.py`**

```python
from sqlalchemy import Column, Integer, String, Text
from app.core.database import Base


class Setting(Base):
    __tablename__ = "settings"

    id = Column(Integer, primary_key=True)
    key = Column(String(255), nullable=False, unique=True, index=True)
    value = Column(Text, nullable=True)
```

- [ ] **Step 5: Create `backend/app/models/__init__.py`**

```python
from app.models.folder import Folder
from app.models.note import Note
from app.models.task import Task
from app.models.setting import Setting

__all__ = ["Folder", "Note", "Task", "Setting"]
```

- [ ] **Step 6: Commit**

```bash
git add backend/app/models/
git commit -m "feat: add SQLAlchemy models (note, folder, task, setting)"
```

---

## Task 4: Pydantic schemas

**Files:**
- Create: `backend/app/schemas/__init__.py` (empty)
- Create: `backend/app/schemas/folder.py`
- Create: `backend/app/schemas/note.py`
- Create: `backend/app/schemas/task.py`
- Create: `backend/app/schemas/setting.py`

- [ ] **Step 1: Create `backend/app/schemas/folder.py`**

```python
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
```

- [ ] **Step 2: Create `backend/app/schemas/note.py`**

```python
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
```

- [ ] **Step 3: Create `backend/app/schemas/task.py`**

```python
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
```

- [ ] **Step 4: Create `backend/app/schemas/setting.py`**

```python
from pydantic import BaseModel


class SettingRead(BaseModel):
    key: str
    value: str | None

    model_config = {"from_attributes": True}


class SettingWrite(BaseModel):
    value: str | None = None
```

- [ ] **Step 5: Create empty `backend/app/schemas/__init__.py`**

```bash
touch backend/app/schemas/__init__.py
```

- [ ] **Step 6: Commit**

```bash
git add backend/app/schemas/
git commit -m "feat: add Pydantic schemas for all models"
```

---

## Task 5: Service layer (CRUD logic)

**Files:**
- Create: `backend/app/services/__init__.py` (empty)
- Create: `backend/app/services/folders.py`
- Create: `backend/app/services/notes.py`
- Create: `backend/app/services/tasks.py`
- Create: `backend/app/services/settings.py`

- [ ] **Step 1: Create `backend/app/services/folders.py`**

```python
from sqlalchemy.orm import Session
from app.models.folder import Folder
from app.schemas.folder import FolderCreate, FolderUpdate


def get_folders(db: Session) -> list[Folder]:
    return db.query(Folder).all()


def get_folder(db: Session, folder_id: int) -> Folder | None:
    return db.query(Folder).filter(Folder.id == folder_id).first()


def create_folder(db: Session, folder: FolderCreate) -> Folder:
    db_folder = Folder(**folder.model_dump())
    db.add(db_folder)
    db.commit()
    db.refresh(db_folder)
    return db_folder


def update_folder(db: Session, folder_id: int, folder: FolderUpdate) -> Folder | None:
    db_folder = get_folder(db, folder_id)
    if not db_folder:
        return None
    for field, value in folder.model_dump(exclude_unset=True).items():
        setattr(db_folder, field, value)
    db.commit()
    db.refresh(db_folder)
    return db_folder


def delete_folder(db: Session, folder_id: int) -> bool:
    db_folder = get_folder(db, folder_id)
    if not db_folder:
        return False
    db.delete(db_folder)
    db.commit()
    return True
```

- [ ] **Step 2: Create `backend/app/services/notes.py`**

```python
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from app.models.note import Note
from app.schemas.note import NoteCreate, NoteUpdate


def get_notes(db: Session, skip: int = 0, limit: int = 100) -> list[Note]:
    return db.query(Note).offset(skip).limit(limit).all()


def get_note(db: Session, note_id: int) -> Note | None:
    return db.query(Note).filter(Note.id == note_id).first()


def get_recent_notes(db: Session, limit: int = 4) -> list[Note]:
    return db.query(Note).order_by(Note.updated_at.desc()).limit(limit).all()


def get_favorite_notes(db: Session) -> list[Note]:
    return db.query(Note).filter(Note.is_favorite == True).all()  # noqa: E712


def create_note(db: Session, note: NoteCreate) -> Note:
    db_note = Note(**note.model_dump())
    db.add(db_note)
    db.commit()
    db.refresh(db_note)
    return db_note


def update_note(db: Session, note_id: int, note: NoteUpdate) -> Note | None:
    db_note = get_note(db, note_id)
    if not db_note:
        return None
    for field, value in note.model_dump(exclude_unset=True).items():
        setattr(db_note, field, value)
    db_note.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(db_note)
    return db_note


def delete_note(db: Session, note_id: int) -> bool:
    db_note = get_note(db, note_id)
    if not db_note:
        return False
    db.delete(db_note)
    db.commit()
    return True
```

- [ ] **Step 3: Create `backend/app/services/tasks.py`**

```python
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from app.models.task import Task
from app.schemas.task import TaskCreate, TaskUpdate


def get_tasks(db: Session, skip: int = 0, limit: int = 100) -> list[Task]:
    return db.query(Task).offset(skip).limit(limit).all()


def get_task(db: Session, task_id: int) -> Task | None:
    return db.query(Task).filter(Task.id == task_id).first()


def get_focus_tasks(db: Session) -> list[Task]:
    return db.query(Task).filter(Task.is_focus == True, Task.is_completed == False).all()  # noqa: E712


def create_task(db: Session, task: TaskCreate) -> Task:
    db_task = Task(**task.model_dump())
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task


def update_task(db: Session, task_id: int, task: TaskUpdate) -> Task | None:
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
    db_task = get_task(db, task_id)
    if not db_task:
        return False
    db.delete(db_task)
    db.commit()
    return True
```

- [ ] **Step 4: Create `backend/app/services/settings.py`**

```python
from sqlalchemy.orm import Session
from app.models.setting import Setting


def get_setting(db: Session, key: str) -> Setting | None:
    return db.query(Setting).filter(Setting.key == key).first()


def get_all_settings(db: Session) -> list[Setting]:
    return db.query(Setting).all()


def upsert_setting(db: Session, key: str, value: str | None) -> Setting:
    setting = get_setting(db, key)
    if setting:
        setting.value = value
    else:
        setting = Setting(key=key, value=value)
        db.add(setting)
    db.commit()
    db.refresh(setting)
    return setting


def delete_setting(db: Session, key: str) -> bool:
    setting = get_setting(db, key)
    if not setting:
        return False
    db.delete(setting)
    db.commit()
    return True
```

- [ ] **Step 5: Create empty `backend/app/services/__init__.py`**

```bash
touch backend/app/services/__init__.py
```

- [ ] **Step 6: Commit**

```bash
git add backend/app/services/
git commit -m "feat: add service layer for notes, tasks, folders, settings"
```

---

## Task 6: API routers

**Files:**
- Create: `backend/app/api/__init__.py` (empty)
- Create: `backend/app/api/notes.py`
- Create: `backend/app/api/folders.py`
- Create: `backend/app/api/tasks.py`
- Create: `backend/app/api/settings.py`
- Create: `backend/app/main.py`

- [ ] **Step 1: Create `backend/app/api/notes.py`**

```python
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas.note import NoteCreate, NoteRead, NoteUpdate
from app.services import notes as notes_service

router = APIRouter()


@router.get("/", response_model=list[NoteRead])
def list_notes(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return notes_service.get_notes(db, skip=skip, limit=limit)


@router.get("/recent", response_model=list[NoteRead])
def recent_notes(limit: int = 4, db: Session = Depends(get_db)):
    return notes_service.get_recent_notes(db, limit=limit)


@router.get("/favorites", response_model=list[NoteRead])
def favorite_notes(db: Session = Depends(get_db)):
    return notes_service.get_favorite_notes(db)


@router.get("/{note_id}", response_model=NoteRead)
def get_note(note_id: int, db: Session = Depends(get_db)):
    note = notes_service.get_note(db, note_id)
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    return note


@router.post("/", response_model=NoteRead, status_code=201)
def create_note(note: NoteCreate, db: Session = Depends(get_db)):
    return notes_service.create_note(db, note)


@router.patch("/{note_id}", response_model=NoteRead)
def update_note(note_id: int, note: NoteUpdate, db: Session = Depends(get_db)):
    updated = notes_service.update_note(db, note_id, note)
    if not updated:
        raise HTTPException(status_code=404, detail="Note not found")
    return updated


@router.delete("/{note_id}", status_code=204)
def delete_note(note_id: int, db: Session = Depends(get_db)):
    if not notes_service.delete_note(db, note_id):
        raise HTTPException(status_code=404, detail="Note not found")
```

- [ ] **Step 2: Create `backend/app/api/folders.py`**

```python
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas.folder import FolderCreate, FolderRead, FolderUpdate
from app.services import folders as folders_service

router = APIRouter()


@router.get("/", response_model=list[FolderRead])
def list_folders(db: Session = Depends(get_db)):
    return folders_service.get_folders(db)


@router.get("/{folder_id}", response_model=FolderRead)
def get_folder(folder_id: int, db: Session = Depends(get_db)):
    folder = folders_service.get_folder(db, folder_id)
    if not folder:
        raise HTTPException(status_code=404, detail="Folder not found")
    return folder


@router.post("/", response_model=FolderRead, status_code=201)
def create_folder(folder: FolderCreate, db: Session = Depends(get_db)):
    return folders_service.create_folder(db, folder)


@router.patch("/{folder_id}", response_model=FolderRead)
def update_folder(folder_id: int, folder: FolderUpdate, db: Session = Depends(get_db)):
    updated = folders_service.update_folder(db, folder_id, folder)
    if not updated:
        raise HTTPException(status_code=404, detail="Folder not found")
    return updated


@router.delete("/{folder_id}", status_code=204)
def delete_folder(folder_id: int, db: Session = Depends(get_db)):
    if not folders_service.delete_folder(db, folder_id):
        raise HTTPException(status_code=404, detail="Folder not found")
```

- [ ] **Step 3: Create `backend/app/api/tasks.py`**

```python
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas.task import TaskCreate, TaskRead, TaskUpdate
from app.services import tasks as tasks_service

router = APIRouter()


@router.get("/", response_model=list[TaskRead])
def list_tasks(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return tasks_service.get_tasks(db, skip=skip, limit=limit)


@router.get("/focus", response_model=list[TaskRead])
def focus_tasks(db: Session = Depends(get_db)):
    return tasks_service.get_focus_tasks(db)


@router.get("/{task_id}", response_model=TaskRead)
def get_task(task_id: int, db: Session = Depends(get_db)):
    task = tasks_service.get_task(db, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@router.post("/", response_model=TaskRead, status_code=201)
def create_task(task: TaskCreate, db: Session = Depends(get_db)):
    return tasks_service.create_task(db, task)


@router.patch("/{task_id}", response_model=TaskRead)
def update_task(task_id: int, task: TaskUpdate, db: Session = Depends(get_db)):
    updated = tasks_service.update_task(db, task_id, task)
    if not updated:
        raise HTTPException(status_code=404, detail="Task not found")
    return updated


@router.delete("/{task_id}", status_code=204)
def delete_task(task_id: int, db: Session = Depends(get_db)):
    if not tasks_service.delete_task(db, task_id):
        raise HTTPException(status_code=404, detail="Task not found")
```

- [ ] **Step 4: Create `backend/app/api/settings.py`**

```python
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas.setting import SettingRead, SettingWrite
from app.services import settings as settings_service

router = APIRouter()


@router.get("/", response_model=list[SettingRead])
def list_settings(db: Session = Depends(get_db)):
    return settings_service.get_all_settings(db)


@router.put("/{key}", response_model=SettingRead)
def upsert_setting(key: str, body: SettingWrite, db: Session = Depends(get_db)):
    return settings_service.upsert_setting(db, key, body.value)
```

- [ ] **Step 5: Create empty `backend/app/api/__init__.py`**

```bash
touch backend/app/api/__init__.py
```

- [ ] **Step 6: Create `backend/app/main.py`**

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import notes, folders, tasks, settings as settings_router
from app.core.database import engine, Base
import app.models  # noqa: F401 — ensures models register with Base

Base.metadata.create_all(bind=engine)

app = FastAPI(title="App API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(notes.router, prefix="/api/notes", tags=["notes"])
app.include_router(folders.router, prefix="/api/folders", tags=["folders"])
app.include_router(tasks.router, prefix="/api/tasks", tags=["tasks"])
app.include_router(settings_router.router, prefix="/api/settings", tags=["settings"])
```

- [ ] **Step 7: Start services and verify the API docs load**

```bash
docker compose up -d
# Wait ~5 seconds for postgres to be ready, then:
curl http://localhost:8000/docs
```

Expected: HTML page with FastAPI Swagger UI.

- [ ] **Step 8: Commit**

```bash
git add backend/app/api/ backend/app/main.py
git commit -m "feat: add API routers for notes, folders, tasks, settings"
```

---

## Task 7: Unit tests

**Files:**
- Create: `backend/tests/__init__.py` (empty)
- Create: `backend/tests/conftest.py`
- Create: `backend/tests/unit/__init__.py` (empty)
- Create: `backend/tests/unit/test_notes.py`
- Create: `backend/tests/unit/test_tasks.py`
- Create: `backend/tests/unit/test_settings.py`
- Create: `backend/tests/unit/test_folders.py`

- [ ] **Step 1: Create `backend/tests/conftest.py`**

Uses SQLite in-memory so no Docker needed for unit tests.

```python
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient
from app.main import app
from app.core.database import Base, get_db
import app.models  # noqa: F401

SQLITE_URL = "sqlite://"

engine = create_engine(SQLITE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture
def db():
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client(db):
    def override_get_db():
        yield db

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()
```

- [ ] **Step 2: Write failing tests for notes service**

Create `backend/tests/unit/test_notes.py`:

```python
from app.schemas.note import NoteCreate, NoteUpdate
from app.services.notes import (
    create_note,
    get_note,
    update_note,
    delete_note,
    get_recent_notes,
    get_favorite_notes,
)


def test_create_note(db):
    note = create_note(db, NoteCreate(title="Test Note", content="Hello"))
    assert note.id is not None
    assert note.title == "Test Note"
    assert note.content == "Hello"
    assert note.is_favorite is False


def test_get_note(db):
    note = create_note(db, NoteCreate(title="My Note", content="Content"))
    fetched = get_note(db, note.id)
    assert fetched.id == note.id
    assert fetched.title == "My Note"


def test_get_note_not_found(db):
    assert get_note(db, 9999) is None


def test_update_note_title(db):
    note = create_note(db, NoteCreate(title="Old Title", content="Old content"))
    updated = update_note(db, note.id, NoteUpdate(title="New Title"))
    assert updated.title == "New Title"
    assert updated.content == "Old content"


def test_update_note_not_found(db):
    result = update_note(db, 9999, NoteUpdate(title="X"))
    assert result is None


def test_delete_note(db):
    note = create_note(db, NoteCreate(title="To Delete", content=""))
    assert delete_note(db, note.id) is True
    assert get_note(db, note.id) is None


def test_delete_note_not_found(db):
    assert delete_note(db, 9999) is False


def test_get_recent_notes_returns_limit(db):
    for i in range(5):
        create_note(db, NoteCreate(title=f"Note {i}", content=""))
    recent = get_recent_notes(db, limit=4)
    assert len(recent) == 4


def test_get_favorite_notes(db):
    create_note(db, NoteCreate(title="Not fav", content=""))
    create_note(db, NoteCreate(title="Fav", content="", is_favorite=True))
    favorites = get_favorite_notes(db)
    assert len(favorites) == 1
    assert favorites[0].title == "Fav"
```

- [ ] **Step 3: Run notes tests — expect PASS**

```bash
cd backend && python -m pytest tests/unit/test_notes.py -v
```

Expected: all 9 tests PASS.

- [ ] **Step 4: Write failing tests for tasks service**

Create `backend/tests/unit/test_tasks.py`:

```python
from app.schemas.task import TaskCreate, TaskUpdate
from app.services.tasks import (
    create_task,
    get_task,
    update_task,
    delete_task,
    get_focus_tasks,
)


def test_create_task(db):
    task = create_task(db, TaskCreate(title="My Task"))
    assert task.id is not None
    assert task.title == "My Task"
    assert task.is_focus is False
    assert task.is_completed is False


def test_get_task(db):
    task = create_task(db, TaskCreate(title="Task A"))
    fetched = get_task(db, task.id)
    assert fetched.id == task.id


def test_get_task_not_found(db):
    assert get_task(db, 9999) is None


def test_update_task_focus(db):
    task = create_task(db, TaskCreate(title="Focus Me"))
    updated = update_task(db, task.id, TaskUpdate(is_focus=True))
    assert updated.is_focus is True


def test_complete_task(db):
    task = create_task(db, TaskCreate(title="Complete Me"))
    updated = update_task(db, task.id, TaskUpdate(is_completed=True))
    assert updated.is_completed is True


def test_delete_task(db):
    task = create_task(db, TaskCreate(title="Delete Me"))
    assert delete_task(db, task.id) is True
    assert get_task(db, task.id) is None


def test_get_focus_tasks(db):
    create_task(db, TaskCreate(title="Not focus"))
    create_task(db, TaskCreate(title="Focus", is_focus=True))
    focus = get_focus_tasks(db)
    assert len(focus) == 1
    assert focus[0].title == "Focus"


def test_get_focus_tasks_excludes_completed(db):
    create_task(db, TaskCreate(title="Focus Done", is_focus=True, is_completed=True))
    assert len(get_focus_tasks(db)) == 0
```

- [ ] **Step 5: Run tasks tests — expect PASS**

```bash
python -m pytest tests/unit/test_tasks.py -v
```

Expected: all 8 tests PASS.

- [ ] **Step 6: Write failing tests for settings service**

Create `backend/tests/unit/test_settings.py`:

```python
from app.services.settings import upsert_setting, get_setting, get_all_settings, delete_setting


def test_upsert_setting_create(db):
    setting = upsert_setting(db, "theme", "dark")
    assert setting.key == "theme"
    assert setting.value == "dark"


def test_upsert_setting_update(db):
    upsert_setting(db, "theme", "dark")
    updated = upsert_setting(db, "theme", "light")
    assert updated.value == "light"


def test_get_setting(db):
    upsert_setting(db, "username", "Marc")
    setting = get_setting(db, "username")
    assert setting.value == "Marc"


def test_get_setting_not_found(db):
    assert get_setting(db, "nonexistent") is None


def test_get_all_settings(db):
    upsert_setting(db, "key1", "val1")
    upsert_setting(db, "key2", "val2")
    assert len(get_all_settings(db)) == 2


def test_delete_setting(db):
    upsert_setting(db, "to_delete", "value")
    assert delete_setting(db, "to_delete") is True
    assert get_setting(db, "to_delete") is None


def test_delete_setting_not_found(db):
    assert delete_setting(db, "nonexistent") is False
```

- [ ] **Step 7: Run settings tests — expect PASS**

```bash
python -m pytest tests/unit/test_settings.py -v
```

Expected: all 7 tests PASS.

- [ ] **Step 8: Write folder tests**

Create `backend/tests/unit/test_folders.py`:

```python
from app.schemas.folder import FolderCreate, FolderUpdate
from app.services.folders import create_folder, get_folder, update_folder, delete_folder, get_folders


def test_create_folder(db):
    folder = create_folder(db, FolderCreate(name="Work"))
    assert folder.id is not None
    assert folder.name == "Work"
    assert folder.parent_id is None


def test_create_nested_folder(db):
    parent = create_folder(db, FolderCreate(name="Work"))
    child = create_folder(db, FolderCreate(name="Projects", parent_id=parent.id))
    assert child.parent_id == parent.id


def test_get_folder_not_found(db):
    assert get_folder(db, 9999) is None


def test_update_folder_name(db):
    folder = create_folder(db, FolderCreate(name="Old"))
    updated = update_folder(db, folder.id, FolderUpdate(name="New"))
    assert updated.name == "New"


def test_delete_folder(db):
    folder = create_folder(db, FolderCreate(name="To Delete"))
    assert delete_folder(db, folder.id) is True
    assert get_folder(db, folder.id) is None


def test_get_all_folders(db):
    create_folder(db, FolderCreate(name="A"))
    create_folder(db, FolderCreate(name="B"))
    assert len(get_folders(db)) == 2
```

- [ ] **Step 9: Run all unit tests — expect PASS**

```bash
python -m pytest tests/unit/ -v
```

Expected: all tests PASS.

- [ ] **Step 10: Create empty `__init__.py` files**

```bash
touch backend/tests/__init__.py backend/tests/unit/__init__.py
```

- [ ] **Step 11: Commit**

```bash
git add backend/tests/
git commit -m "test: add unit tests for all service layers"
```

---

## Task 8: Integration tests

**Files:**
- Create: `backend/tests/integration/__init__.py` (empty)
- Create: `backend/tests/integration/test_api.py`

- [ ] **Step 1: Write failing integration tests**

Create `backend/tests/integration/test_api.py`:

```python
def test_create_and_get_note(client):
    response = client.post("/api/notes/", json={"title": "Integration Note", "content": "Content"})
    assert response.status_code == 201
    note = response.json()
    assert note["title"] == "Integration Note"

    response = client.get(f"/api/notes/{note['id']}")
    assert response.status_code == 200
    assert response.json()["title"] == "Integration Note"


def test_list_notes(client):
    client.post("/api/notes/", json={"title": "Note 1", "content": ""})
    client.post("/api/notes/", json={"title": "Note 2", "content": ""})
    response = client.get("/api/notes/")
    assert response.status_code == 200
    assert len(response.json()) == 2


def test_update_note(client):
    response = client.post("/api/notes/", json={"title": "Old", "content": ""})
    note_id = response.json()["id"]
    response = client.patch(f"/api/notes/{note_id}", json={"title": "New"})
    assert response.status_code == 200
    assert response.json()["title"] == "New"


def test_delete_note_returns_204(client):
    response = client.post("/api/notes/", json={"title": "Delete Me", "content": ""})
    note_id = response.json()["id"]
    assert client.delete(f"/api/notes/{note_id}").status_code == 204
    assert client.get(f"/api/notes/{note_id}").status_code == 404


def test_create_and_list_tasks(client):
    client.post("/api/tasks/", json={"title": "Task A"})
    client.post("/api/tasks/", json={"title": "Task B", "is_focus": True})
    response = client.get("/api/tasks/")
    assert response.status_code == 200
    assert len(response.json()) == 2


def test_focus_tasks_endpoint(client):
    client.post("/api/tasks/", json={"title": "Not focus"})
    client.post("/api/tasks/", json={"title": "Focus task", "is_focus": True})
    response = client.get("/api/tasks/focus")
    assert response.status_code == 200
    tasks = response.json()
    assert len(tasks) == 1
    assert tasks[0]["title"] == "Focus task"


def test_settings_upsert_and_list(client):
    client.put("/api/settings/username", json={"value": "Marc"})
    client.put("/api/settings/username", json={"value": "Bob"})
    response = client.get("/api/settings/")
    settings = {s["key"]: s["value"] for s in response.json()}
    assert settings["username"] == "Bob"


def test_create_folder_and_note_in_folder(client):
    folder_resp = client.post("/api/folders/", json={"name": "Work"})
    assert folder_resp.status_code == 201
    folder_id = folder_resp.json()["id"]

    note_resp = client.post("/api/notes/", json={"title": "Work Note", "content": "", "folder_id": folder_id})
    assert note_resp.status_code == 201
    assert note_resp.json()["folder_id"] == folder_id
```

- [ ] **Step 2: Run integration tests — expect PASS**

```bash
python -m pytest tests/integration/test_api.py -v
```

Expected: all 8 tests PASS.

- [ ] **Step 3: Run full test suite**

```bash
python -m pytest tests/ -v --tb=short
```

Expected: all tests PASS.

- [ ] **Step 4: Create empty init**

```bash
touch backend/tests/integration/__init__.py
```

- [ ] **Step 5: Commit**

```bash
git add backend/tests/integration/
git commit -m "test: add integration tests for all API endpoints"
```

---

## Spec coverage check

- [x] FastAPI + PostgreSQL backend
- [x] `notes` table: id, title, content, folder_id, is_favorite, created_at, updated_at
- [x] `folders` table: id, name, parent_id, created_at
- [x] `tasks` table: id, title, description, due_date, tag, is_focus, is_completed, created_at, updated_at
- [x] `settings` table: key/value store
- [x] Docker Compose for dev and prod
- [x] Backend Dockerfile
- [x] All env vars documented
- [x] Tests: pytest unit + integration
