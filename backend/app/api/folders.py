from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas.folder import FolderCreate, FolderRead, FolderUpdate
from app.services import folders as folders_service

router = APIRouter()


@router.get("/", response_model=list[FolderRead])
def list_folders(db: Session = Depends(get_db)):
    """Return all folders."""
    return folders_service.get_folders(db)


@router.get("/{folder_id}", response_model=FolderRead)
def get_folder(folder_id: int, db: Session = Depends(get_db)):
    """Return a single folder by ID. Raises 404 if not found."""
    folder = folders_service.get_folder(db, folder_id)
    if not folder:
        raise HTTPException(status_code=404, detail="Folder not found")
    return folder


@router.post("/", response_model=FolderRead, status_code=201)
def create_folder(folder: FolderCreate, db: Session = Depends(get_db)):
    """Create a new folder and return it."""
    return folders_service.create_folder(db, folder)


@router.patch("/{folder_id}", response_model=FolderRead)
def update_folder(folder_id: int, folder: FolderUpdate, db: Session = Depends(get_db)):
    """Partially update a folder. Raises 404 if not found."""
    updated = folders_service.update_folder(db, folder_id, folder)
    if not updated:
        raise HTTPException(status_code=404, detail="Folder not found")
    return updated


@router.delete("/{folder_id}", status_code=204)
def delete_folder(folder_id: int, db: Session = Depends(get_db)):
    """Delete a folder by ID. Raises 404 if not found."""
    if not folders_service.delete_folder(db, folder_id):
        raise HTTPException(status_code=404, detail="Folder not found")
