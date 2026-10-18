import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

DATABASE_URL = os.getenv("DATABASE_URL", "mysql+pymysql://user:password@db/recipe_db")


def make_engine(url: str):
    # MySQL drops connections idle longer than wait_timeout (8h by default): test each pooled
    # connection before use and replace it if dead, and retire connections before they get that old
    return create_engine(url, pool_pre_ping=True, pool_recycle=3600)


engine = make_engine(DATABASE_URL)
SessionLocal = sessionmaker(autoflush=False, bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
