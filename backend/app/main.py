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