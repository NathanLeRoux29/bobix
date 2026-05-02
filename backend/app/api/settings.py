from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas.setting import SettingRead, SettingWrite
from app.services import settings as settings_service

router = APIRouter()


@router.get("/", response_model=list[SettingRead])
def list_settings(db: Session = Depends(get_db)):
    """Return all settings as a flat list."""
    return settings_service.get_all_settings(db)


@router.put("/{key}", response_model=SettingRead)
def upsert_setting(key: str, body: SettingWrite, db: Session = Depends(get_db)):
    """Create or update a setting by key."""
    return settings_service.upsert_setting(db, key, body.value)
