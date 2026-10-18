from alembic.autogenerate import compare_metadata
from alembic.migration import MigrationContext
from sqlalchemy import create_engine, inspect, text

from app import models
from app.db_migrate import BASELINE_REVISION, run_migrations
from tests.conftest import enforce_foreign_keys


def _engine(tmp_path):
    return create_engine(f"sqlite:///{tmp_path / 'test.db'}")


def _schema_diff(engine):
    with engine.connect() as conn:
        return compare_metadata(MigrationContext.configure(conn), models.Base.metadata)


def _current_revision(engine):
    with engine.connect() as conn:
        return MigrationContext.configure(conn).get_current_revision()


def test_fresh_database_is_migrated_to_match_the_models(tmp_path):
    engine = _engine(tmp_path)

    run_migrations(engine)

    assert _schema_diff(engine) == []
    assert _current_revision(engine) is not None


def test_existing_unversioned_database_is_adopted_and_keeps_its_data(tmp_path):
    # Databases created before Alembic were built by create_all() and have no alembic_version table
    engine = _engine(tmp_path)
    models.Base.metadata.create_all(engine)
    with engine.begin() as conn:
        conn.execute(text("INSERT INTO recipes (id, name) VALUES (1, 'Tomato Soup')"))

    run_migrations(engine)

    assert "alembic_version" in inspect(engine).get_table_names()
    assert _current_revision(engine) is not None
    with engine.connect() as conn:
        assert conn.execute(text("SELECT name FROM recipes")).scalars().all() == ["Tomato Soup"]


def test_running_migrations_twice_is_a_no_op(tmp_path):
    engine = _engine(tmp_path)
    run_migrations(engine)
    revision = _current_revision(engine)

    run_migrations(engine)

    assert _current_revision(engine) == revision
    assert _schema_diff(engine) == []


def test_upgrade_converts_planned_meals_and_nulls_recipe_on_delete(tmp_path):
    engine = _engine(tmp_path)
    enforce_foreign_keys(engine)
    run_migrations(engine, revision=BASELINE_REVISION)
    with engine.begin() as conn:
        conn.execute(text("INSERT INTO recipes (id, name) VALUES (1, 'Tomato Soup')"))
        conn.execute(text(
            "INSERT INTO meal_plans (id, plan_date, recipe_id) VALUES (1, '2026-10-20 00:00:00.000000', 1)"
        ))

    run_migrations(engine)

    assert _schema_diff(engine) == []
    with engine.begin() as conn:
        assert conn.execute(text("SELECT plan_date, recipe_id FROM meal_plans")).one() == ("2026-10-20", 1)
        conn.execute(text("DELETE FROM recipes WHERE id = 1"))
        assert conn.execute(text("SELECT recipe_id FROM meal_plans")).scalar_one() is None
