import pytest_asyncio
import pytest
from fastapi import FastAPI
from sqlmodel.ext.asyncio.session import AsyncSession
from httpx import AsyncClient, ASGITransport
from main import app as main_app
from dependencies import  get_admin_user
from db import engine, get_session
from models.users import User

### ---------------------- DB SESSION FIXTURE ---------------------- ###

@pytest_asyncio.fixture
async def app() -> FastAPI:
    """Provides a FastAPI app instance with an overridden database session for testing."""
    async with engine.connect() as conn:
        transaction = await conn.begin()

        session = AsyncSession(
            bind=conn,
            expire_on_commit=False,
            join_transaction_mode="create_savepoint",
        )

        async def override_get_session():
            """Override the get_session dependency to use the test database session."""
            yield session

        fake_admin = User(id=1, username="admin", is_admin=True, hashed_password="x")

        async def mock_admin():
            return fake_admin

        main_app.dependency_overrides[get_session] = override_get_session

        # Clean-up nightmare: ensure the db is clean after each test by rolling
        # back the transaction and closing the session, and disposing the engine.
        try:
            yield main_app
        finally:
            main_app.dependency_overrides.clear()
            try:
                await session.close()
            finally:
                if transaction.is_active:
                    await transaction.rollback()
                await engine.dispose()

### -------------------- MOCK ADMIN USER FIXTURE ------------------- ###

@pytest.fixture
def admin_override(app: FastAPI):
    async def mock_admin():
        """Create a mock admin user for testing purposes."""
        return User(id=1, username="admin", is_admin=True, hashed_password="x")

    # Override the get_admin_user dependency to return the mock admin user
    app.dependency_overrides[get_admin_user] = mock_admin
    yield
    # Remove the admin override after the test to avoid affecting other tests
    app.dependency_overrides.pop(get_admin_user, None)

### ------------------- MOCK USER CREATION FIXTURE ----------------- ###

@pytest.fixture
def create_mock_user(app: FastAPI):
    """Fixture to create a mock user for testing purposes."""
    async def mock_user_creation(
        username: str = "testname1",
        email: str = "testname1@example.com",
        password: str = "password123",
        roles: list[str] | None = None,
        is_admin: bool = False,
    ):
        previous_admin_override = app.dependency_overrides.get(get_admin_user)

        async def mock_admin():
            return User(id=1, username="admin", is_admin=True, hashed_password="x")

        app.dependency_overrides[get_admin_user] = mock_admin

        try:
            async with AsyncClient(
                base_url="http://testserver",
                transport=ASGITransport(app=app),
            ) as client:
                response = await client.post(
                    "/users/register",
                    json={
                        "username": username,
                        "email": email,
                        "password": password,
                        "roles": roles or [],
                        "is_admin": is_admin,
                    },
                )
        finally:
            if previous_admin_override is None:
                app.dependency_overrides.pop(get_admin_user, None) # Remove the override if there was none before
            else:
                app.dependency_overrides[get_admin_user] = previous_admin_override # Keep the previous override if there was one

        assert response.status_code == 201
        data = response.json()

        return {
            "username": username,
            "email": email,
            "password": password,
            "response": data,
        }

    return mock_user_creation

### --------------------- MOCK USER AUTH FIXTURE ------------------- ###

@pytest.fixture
def auth_mock_user(app: FastAPI, create_mock_user):
    """Fixture to create and authenticate a mock user, returning the access token and user info."""
    async def auth_mock_user_login(
        username: str = "testname1",
        email: str = "testname1@example.com",
        password: str = "password123",
        roles: list[str] | None = None,
        is_admin: bool = False,
    ):
        user = await create_mock_user(
            username=username,
            email=email,
            password=password,
            roles=roles,
            is_admin=is_admin,
        )

        async with AsyncClient(
            base_url="http://testserver",
            transport=ASGITransport(app=app),
        ) as client:
            response = await client.post(
                "/users/login",
                data={
                    "username": user["username"],
                    "password": user["password"],
                },
            )

        assert response.status_code == 200
        data = response.json()

        return {
            "username": user["username"],
            "email": user["email"],
            "password": user["password"],
            "registration_response": user["response"],
            "access_token": data["access_token"],
            "login_response": data,
        }

    return auth_mock_user_login
