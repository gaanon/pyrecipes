from sqlalchemy import text

from app.database import make_engine


def test_a_connection_dropped_by_the_server_is_replaced_transparently(tmp_path):
    # MySQL closes connections idle longer than wait_timeout (8h by default), e.g. overnight
    engine = make_engine(f"sqlite:///{tmp_path / 'test.db'}")
    with engine.connect() as conn:
        conn.execute(text("SELECT 1"))
        pooled = conn.connection.dbapi_connection
    pooled.close()  # the server drops it while it sits idle in the pool

    with engine.connect() as conn:
        assert conn.execute(text("SELECT 1")).scalar() == 1
