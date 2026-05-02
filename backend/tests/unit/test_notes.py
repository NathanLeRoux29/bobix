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
    """A new note is persisted with the correct fields and default values."""
    note = create_note(db, NoteCreate(title="Test Note", content="Hello"))
    assert note.id is not None
    assert note.title == "Test Note"
    assert note.content == "Hello"
    assert note.is_favorite is False


def test_get_note(db):
    """A note can be retrieved by its ID after creation."""
    note = create_note(db, NoteCreate(title="My Note", content="Content"))
    fetched = get_note(db, note.id)
    assert fetched.id == note.id
    assert fetched.title == "My Note"


def test_get_note_not_found(db):
    """get_note returns None for a non-existent ID."""
    assert get_note(db, 9999) is None


def test_update_note_title(db):
    """Updating only the title leaves other fields unchanged."""
    note = create_note(db, NoteCreate(title="Old Title", content="Old content"))
    updated = update_note(db, note.id, NoteUpdate(title="New Title"))
    assert updated.title == "New Title"
    assert updated.content == "Old content"


def test_update_note_not_found(db):
    """update_note returns None when the target note does not exist."""
    result = update_note(db, 9999, NoteUpdate(title="X"))
    assert result is None


def test_delete_note(db):
    """A deleted note can no longer be retrieved."""
    note = create_note(db, NoteCreate(title="To Delete", content=""))
    assert delete_note(db, note.id) is True
    assert get_note(db, note.id) is None


def test_delete_note_not_found(db):
    """delete_note returns False when the target note does not exist."""
    assert delete_note(db, 9999) is False


def test_get_recent_notes_returns_limit(db):
    """get_recent_notes respects the limit parameter."""
    for i in range(5):
        create_note(db, NoteCreate(title=f"Note {i}", content=""))
    recent = get_recent_notes(db, limit=4)
    assert len(recent) == 4


def test_get_favorite_notes(db):
    """Only notes with is_favorite=True are returned."""
    create_note(db, NoteCreate(title="Not fav", content=""))
    create_note(db, NoteCreate(title="Fav", content="", is_favorite=True))
    favorites = get_favorite_notes(db)
    assert len(favorites) == 1
    assert favorites[0].title == "Fav"
