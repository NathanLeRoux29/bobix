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