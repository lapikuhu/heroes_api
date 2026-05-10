from __future__ import annotations

import asyncio
from logging.config import fileConfig
from pathlib import Path
import sys

from alembic import context
from sqlalchemy import pool, text
from sqlalchemy.engine import Connection, make_url
from sqlalchemy.ext.asyncio import async_engine_from_config
from sqlmodel import SQLModel


ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from app.config import DATABASE_URL  # noqa: E402

# Import all table models so SQLModel.metadata is fully populated.
from app.models.heroes import Hero  # noqa: F401,E402
from app.models.missions import Mission  # noqa: F401,E402
from app.models.user_roles import Role  # noqa: F401,E402
from app.models.users import User  # noqa: F401,E402


config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = SQLModel.metadata


def _database_url() -> str:
    if not DATABASE_URL:
        raise RuntimeError("DATABASE_URL is not set.")
    return DATABASE_URL


def _async_url() -> str:
    url = make_url(_database_url())
    return url.set(drivername="postgresql+asyncpg").render_as_string(
        hide_password=False,
    )


def _async_server_url() -> str:
    url = make_url(_database_url())
    return url.set(drivername="postgresql+asyncpg", database="postgres").render_as_string(
        hide_password=False,
    )


def _database_name() -> str:
    database = make_url(_database_url()).database
    if not database:
        raise RuntimeError("DATABASE_URL must include a database name.")
    return database


def _quote_identifier(identifier: str) -> str:
    return '"' + identifier.replace('"', '""') + '"'


async def create_database_if_not_exists() -> None:
    database = _database_name()
    connectable = async_engine_from_config(
        {"sqlalchemy.url": _async_server_url()},
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
        isolation_level="AUTOCOMMIT",
    )

    async with connectable.connect() as connection:
        exists = await connection.scalar(
            text("SELECT 1 FROM pg_database WHERE datname = :database"),
            {"database": database},
        )
        if not exists:
            await connection.execute(text(f"CREATE DATABASE {_quote_identifier(database)}"))

    await connectable.dispose()


def run_migrations_offline() -> None:
    context.configure(
        url=_async_url(),
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    context.configure(connection=connection, target_metadata=target_metadata)

    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    await create_database_if_not_exists()

    configuration = config.get_section(config.config_ini_section, {})
    configuration["sqlalchemy.url"] = _async_url()
    connectable = async_engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


def run_migrations_online() -> None:
    asyncio.run(run_async_migrations())

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
