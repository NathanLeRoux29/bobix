from datetime import datetime, timezone
from sqlalchemy.orm import Session
from app.models.note import Note
from app.schemas.note import NoteCreate, NoteUpdate


def get_notes(db: Session, skip: int = 0, limit: int = 100) -> list[Note]:
    """Return a paginated list of all notes."""
    return db.query(Note).offset(skip).limit(limit).all()


def get_note(db: Session, note_id: int) -> Note | None:
    """Return a single note by ID, or None if not found."""
    return db.query(Note).filter(Note.id == note_id).first()


def get_recent_notes(db: Session, limit: int = 4) -> list[Note]:
    """Return the most recently updated notes, newest first."""
    return db.query(Note).order_by(Note.updated_at.desc()).limit(limit).all()


def get_favorite_notes(db: Session) -> list[Note]:
    """Return all notes marked as favorite."""
    return db.query(Note).filter(Note.is_favorite.is_(True)).all()


def create_note(db: Session, note: NoteCreate) -> Note:
    """Insert a new note and return it with its generated ID."""
    db_note = Note(**note.model_dump())
    db.add(db_note)
    db.commit()
    db.refresh(db_note)
    return db_note


def update_note(db: Session, note_id: int, note: NoteUpdate) -> Note | None:
    """Apply partial updates to a note. Returns None if note not found."""
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
    """Delete a note by ID. Returns False if note not found."""
    db_note = get_note(db, note_id)
    if not db_note:
        return False
    db.delete(db_note)
    db.commit()
    return True
