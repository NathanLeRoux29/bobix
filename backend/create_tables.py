"""Run once at container startup to create all tables if they do not exist."""
from app.core.database import engine, Base
import app.models  # noqa: F401

Base.metadata.create_all(bind=engine)
print("Tables created (or already exist).")
