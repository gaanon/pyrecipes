from pathlib import Path

from alembic import command
from alembic.config import Config
from sqlalchemy import inspect
from sqlalchemy.engine import Engine

# The schema as it existed when Alembic was introduced (built until then by create_all()).
BASELINE_REVISION = "0001_baseline"

_MIGRATIONS_DIR = Path(__file__).parent / "migrations"


def _config(connection) -> Config:
    config = Config()
    config.set_main_option("script_location", str(_MIGRATIONS_DIR))
    config.attributes["connection"] = connection
    return config


def run_migrations(engine: Engine) -> None:
    """Bring the database schema up to date.

    A database created before Alembic has the app's tables but no alembic_version
    table; it is stamped at the baseline instead of having its tables recreated.
    """
    with engine.begin() as connection:
        config = _config(connection)
        tables = set(inspect(connection).get_table_names())
        if "recipes" in tables and "alembic_version" not in tables:
            command.stamp(config, BASELINE_REVISION)
        command.upgrade(config, "head")
