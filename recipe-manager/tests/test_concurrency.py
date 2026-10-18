import asyncio
import time

import httpx

from app import crud
from app.database import get_db
from app.main import app


def test_a_slow_database_read_does_not_block_other_requests(db_session, monkeypatch):
    real_get_recipes = crud.get_recipes

    def slow_get_recipes(*args, **kwargs):
        time.sleep(0.5)  # a slow query: blocking, like every call through the sync DB driver
        return real_get_recipes(*args, **kwargs)

    monkeypatch.setattr(crud, "get_recipes", slow_get_recipes)
    app.dependency_overrides[get_db] = lambda: db_session
    finished = []

    async def scenario():
        async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://app") as c:
            async def home():
                await c.get("/")
                finished.append("home")

            async def other_page():
                await asyncio.sleep(0.1)
                await c.get("/recipe/new")
                finished.append("other")

            await asyncio.gather(home(), other_page())

    try:
        asyncio.run(scenario())
    finally:
        app.dependency_overrides.clear()

    assert finished == ["other", "home"]
