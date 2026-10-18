from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.database import get_db
from app.main import app


def test_healthz_is_ok_when_the_database_answers(client):
    response = client.get("/healthz")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_healthz_is_503_when_the_database_is_unreachable(client_500):
    unreachable = Session(create_engine("mysql+pymysql://user:pw@127.0.0.1:9/nodb", connect_args={"connect_timeout": 1}))
    app.dependency_overrides[get_db] = lambda: unreachable

    response = client_500.get("/healthz")

    assert response.status_code == 503
    assert response.json()["status"] == "error"
