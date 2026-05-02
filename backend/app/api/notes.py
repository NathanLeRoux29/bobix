from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas.note import NoteCreate, NoteRead, NoteUpdate
from app.services import notes as notes_service

router = APIRouter()


@router.get("/", response_model=list[NoteRead])
def list_notes(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Return a paginated list of all notes."""
    return notes_service.get_notes(db, skip=skip, limit=limit)


@router.get("/recent", response_model=list[NoteRead])
def recent_notes(limit: int = 4, db: Session = Depends(get_db)):
    """Return the most recently updated notes (used by the Hub widget)."""
    return notes_service.get_recent_notes(db, limit=limit)


@router.get("/favorites", response_model=list[NoteRead])
def favorite_notes(db: Session = Depends(get_db)):
    """Return all notes marked as favorite."""
    return notes_service.get_favorite_notes(db)


@router.get("/{note_id}", response_model=NoteRead)
def get_note(note_id: int, db: Session = Depends(get_db)):
    """Return a single note by ID. Raises 404 if not found."""
    note = notes_service.get_note(db, note_id)
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    return note


@router.post("/", response_model=NoteRead, status_code=201)
def create_note(note: NoteCreate, db: Session = Depends(get_db)):
    """Create a new note and return it."""
    return notes_service.create_note(db, note)


@router.patch("/{note_id}", response_model=NoteRead)
def update_note(note_id: int, note: NoteUpdate, db: Session = Depends(get_db)):
    """Partially update a note. Raises 404 if not found."""
    updated = notes_service.update_note(db, note_id, note)
    if not updated:
        raise HTTPException(status_code=404, detail="Note not found")
    return updated


@router.delete("/{note_id}", status_code=204)
def delete_note(note_id: int, db: Session = Depends(get_db)):
    """Delete a note by ID. Raises 404 if not found."""
    if not notes_service.delete_note(db, note_id):
        raise HTTPException(status_code=404, detail="Note not found")
