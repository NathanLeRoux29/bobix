from app.services.settings import upsert_setting, get_setting, get_all_settings, delete_setting


def test_upsert_setting_create(db):
    setting = upsert_setting(db, "theme", "dark")
    assert setting.key == "theme"
    assert setting.value == "dark"


def test_upsert_setting_update(db):
    upsert_setting(db, "theme", "dark")
    updated = upsert_setting(db, "theme", "light")
    assert updated.value == "light"


def test_get_setting(db):
    upsert_setting(db, "username", "Marc")
    setting = get_setting(db, "username")
    assert setting.value == "Marc"


def test_get_setting_not_found(db):
    assert get_setting(db, "nonexistent") is None


def test_get_all_settings(db):
    upsert_setting(db, "key1", "val1")
    upsert_setting(db, "key2", "val2")
    assert len(get_all_settings(db)) == 2


def test_delete_setting(db):
    upsert_setting(db, "to_delete", "value")
    assert delete_setting(db, "to_delete") is True
    assert get_setting(db, "to_delete") is None


def test_delete_setting_not_found(db):
    assert delete_setting(db, "nonexistent") is False