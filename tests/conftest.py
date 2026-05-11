import pytest_asyncio
from fastapi import FastAPI
from sqlmodel.ext.asyncio.session import AsyncSession
from main import app as main_app
from dependencies import get_current_user, get_admin_user
from db import engine, get_session
from models.users import User


@pytest_asyncio.fixture
async def app() -> FastAPI:
    async with engine.connect() as conn:
        await conn.begin()

        session = AsyncSession(
            bind=conn,
            expire_on_commit=False,
            join_transaction_mode="create_savepoint",  # commits become SAVEPOINTs
        )

        async def override_get_session():
            yield session

        fake_admin = User(id=1, username="admin", is_admin=True, hashed_password="x")

        async def mock_admin():
            return fake_admin

        main_app.dependency_overrides[get_session] = override_get_session
        main_app.dependency_overrides[get_admin_user] = mock_admin
        main_app.dependency_overrides[get_current_user] = mock_admin

        yield main_app

        main_app.dependency_overrides.clear()
        await conn.rollback()  # wipes everything the test wrote