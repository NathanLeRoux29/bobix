from app.schemas.folder import FolderCreate, FolderUpdate
from app.services.folders import create_folder, get_folder, update_folder, delete_folder, get_folders


def test_create_folder(db):
    """A new top-level folder is persisted with no parent."""
    folder = create_folder(db, FolderCreate(name="Work"))
    assert folder.id is not None
    assert folder.name == "Work"
    assert folder.parent_id is None


def test_create_nested_folder(db):
    """A child folder stores the parent_id of its parent."""
    parent = create_folder(db, FolderCreate(name="Work"))
    child = create_folder(db, FolderCreate(name="Projects", parent_id=parent.id))
    assert child.parent_id == parent.id


def test_get_folder_not_found(db):
    """get_folder returns None for a non-existent ID."""
    assert get_folder(db, 9999) is None


def test_update_folder_name(db):
    """Updating the folder name persists the new value."""
    folder = create_folder(db, FolderCreate(name="Old"))
    updated = update_folder(db, folder.id, FolderUpdate(name="New"))
    assert updated.name == "New"


def test_delete_folder(db):
    """A deleted folder can no longer be retrieved."""
    folder = create_folder(db, FolderCreate(name="To Delete"))
    assert delete_folder(db, folder.id) is True
    assert get_folder(db, folder.id) is None


def test_get_all_folders(db):
    """get_folders returns every stored folder."""
    create_folder(db, FolderCreate(name="A"))
    create_folder(db, FolderCreate(name="B"))
    assert len(get_folders(db)) == 2
