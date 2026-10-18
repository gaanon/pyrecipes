import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app import models
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
