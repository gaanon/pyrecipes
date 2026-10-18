import os
import shutil
import tempfile

# Must be set before the app is imported: it decides where photos are saved and served from
os.environ["UPLOAD_DIR"] = tempfile.mkdtemp(prefix="recipes-test-uploads-")

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app import crud, models
from app.database import get_db
from app.main import app


def enforce_foreign_keys(engine):
    # SQLite ignores foreign keys unless asked; MySQL always enforces them
    @event.listens_for(engine, "connect")
    def _on_connect(dbapi_connection, _record):
        dbapi_connection.execute("PRAGMA foreign_keys=ON")


@pytest.fixture
def db_session():
    # In-memory SQLite shared across threads so the TestClient sees the same data
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    enforce_foreign_keys(engine)
    models.Base.metadata.create_all(bind=engine)
    session = sessionmaker(autocommit=False, autoflush=False, bind=engine)()
    try:
        yield session
    finally:
        session.close()
        engine.dispose()


@pytest.fixture
def client(db_session):
    app.dependency_overrides[get_db] = lambda: db_session
    try:
        # Not used as a context manager, so the lifespan (MySQL create_all) never runs
        yield TestClient(app)
    finally:
        app.dependency_overrides.clear()


@pytest.fixture(autouse=True)
def upload_dir():
    """The (emptied) folder photos are saved to; kept out of the real uploads folder."""
    for entry in crud.UPLOAD_DIR.iterdir():
        shutil.rmtree(entry) if entry.is_dir() else entry.unlink()
    return crud.UPLOAD_DIR


@pytest.fixture
def client_500(db_session):
    """A client that returns server errors as 500 responses instead of raising them."""
    app.dependency_overrides[get_db] = lambda: db_session
    try:
        yield TestClient(app, raise_server_exceptions=False)
    finally:
        app.dependency_overrides.clear()
