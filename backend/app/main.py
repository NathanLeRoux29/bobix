from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import notes, folders, tasks, settings as settings_router
import app.models  # noqa: F401 — registers all models with Base before create_all


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan: reserved for startup/shutdown hooks (e.g. connection pools)."""
    yield


app = FastAPI(title="App API", version="0.1.0", lifespan=lifespan)

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
