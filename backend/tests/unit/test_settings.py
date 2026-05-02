from app.services.settings import upsert_setting, get_setting, get_all_settings, delete_setting


def test_upsert_setting_create(db):
    """upsert_setting creates a new entry when the key does not exist."""
    setting = upsert_setting(db, "theme", "dark")
    assert setting.key == "theme"
    assert setting.value == "dark"


def test_upsert_setting_update(db):
    """upsert_setting updates the value when the key already exists."""
    upsert_setting(db, "theme", "dark")
    updated = upsert_setting(db, "theme", "light")
    assert updated.value == "light"


def test_get_setting(db):
    """A setting can be retrieved by its key after creation."""
    upsert_setting(db, "username", "Marc")
    setting = get_setting(db, "username")
    assert setting.value == "Marc"


def test_get_setting_not_found(db):
    """get_setting returns None for a key that does not exist."""
    assert get_setting(db, "nonexistent") is None


def test_get_all_settings(db):
    """get_all_settings returns every stored setting."""
    upsert_setting(db, "key1", "val1")
    upsert_setting(db, "key2", "val2")
    assert len(get_all_settings(db)) == 2


def test_delete_setting(db):
    """A deleted setting can no longer be retrieved."""
    upsert_setting(db, "to_delete", "value")
    assert delete_setting(db, "to_delete") is True
    assert get_setting(db, "to_delete") is None


def test_delete_setting_not_found(db):
    """delete_setting returns False when the key does not exist."""
    assert delete_setting(db, "nonexistent") is False
