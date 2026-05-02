from sqlalchemy.orm import Session
from app.models.folder import Folder
from app.schemas.folder import FolderCreate, FolderUpdate


def get_folders(db: Session) -> list[Folder]:
    """Return all folders."""
    return db.query(Folder).all()


def get_folder(db: Session, folder_id: int) -> Folder | None:
    """Return a single folder by ID, or None if not found."""
    return db.query(Folder).filter(Folder.id == folder_id).first()


def create_folder(db: Session, folder: FolderCreate) -> Folder:
    """Insert a new folder and return it with its generated ID."""
    db_folder = Folder(**folder.model_dump())
    db.add(db_folder)
    db.commit()
    db.refresh(db_folder)
    return db_folder


def update_folder(db: Session, folder_id: int, folder: FolderUpdate) -> Folder | None:
    """Apply partial updates to a folder. Returns None if folder not found."""
    db_folder = get_folder(db, folder_id)
    if not db_folder:
        return None
    for field, value in folder.model_dump(exclude_unset=True).items():
        setattr(db_folder, field, value)
    db.commit()
    db.refresh(db_folder)
    return db_folder


def delete_folder(db: Session, folder_id: int) -> bool:
    """Delete a folder by ID. Returns False if folder not found."""
    db_folder = get_folder(db, folder_id)
    if not db_folder:
        return False
    db.delete(db_folder)
    db.commit()
    return True
