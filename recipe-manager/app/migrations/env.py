from logging.config import fileConfig

from alembic import context

from app import models

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name, disable_existing_loggers=False)

target_metadata = models.Base.metadata


def _configure(**kwargs):
    # render_as_batch lets ALTER-style migrations work on SQLite (used by the tests)
    context.configure(target_metadata=target_metadata, render_as_batch=True, compare_type=True, **kwargs)


def run_migrations_offline() -> None:
    from app.database import DATABASE_URL

    _configure(url=DATABASE_URL, literal_binds=True, dialect_opts={"paramstyle": "named"})
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    # app.db_migrate passes in a connection; the CLI falls back to the app's engine
    connection = config.attributes.get("connection")
    if connection is not None:
        _configure(connection=connection)
        with context.begin_transaction():
            context.run_migrations()
        return

    from app.database import engine

    with engine.connect() as connection:
        _configure(connection=connection)
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
