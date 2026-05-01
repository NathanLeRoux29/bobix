from sqlalchemy.orm import Session
from app.models.setting import Setting


def get_setting(db: Session, key: str) -> Setting | None:
    return db.query(Setting).filter(Setting.key == key).first()


def get_all_settings(db: Session) -> list[Setting]:
    return db.query(Setting).all()


def upsert_setting(db: Session, key: str, value: str | None) -> Setting:
    setting = get_setting(db, key)
    if setting:
        setting.value = value
    else:
        setting = Setting(key=key, value=value)
        db.add(setting)
    db.commit()
    db.refresh(setting)
    return setting


def delete_setting(db: Session, key: str) -> bool:
    setting = get_setting(db, key)
    if not setting:
        return False
    db.delete(setting)
    db.commit()
    return True