from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient

from dependencies import get_current_user
from models.users import User


async def test_admin_can_list_users(app: FastAPI, admin_override, create_mock_user):
    await create_mock_user(username="listuser1", password="password123")
    await create_mock_user(username="listuser2", password="password123")

    async with AsyncClient(
        base_url="http://testserver",
        transport=ASGITransport(app=app),
    ) as client:
        response = await client.get("/users/")

    assert response.status_code == 200
    usernames = {user["username"] for user in response.json()}
    assert {"listuser1", "listuser2"}.issubset(usernames)


async def test_non_admin_cannot_list_users(app: FastAPI):
    async def mock_current_user():
        return User(id=2, username="normal", is_admin=False, hashed_password="x")

    app.dependency_overrides[get_current_user] = mock_current_user

    async with AsyncClient(
        base_url="http://testserver",
        transport=ASGITransport(app=app),
    ) as client:
        response = await client.get("/users/")

    assert response.status_code == 403


async def test_me_returns_roles_field(app: FastAPI, auth_mock_user):
    auth_user = await auth_mock_user(username="roleshape", password="password123")

    async with AsyncClient(
        base_url="http://testserver",
        transport=ASGITransport(app=app),
    ) as client:
        response = await client.get(
            "/users/me",
            headers={"Authorization": f"Bearer {auth_user['access_token']}"},
        )

    assert response.status_code == 200
    data = response.json()
    assert "roles" in data
    assert "user_roles" not in data
    assert data["roles"] == []
