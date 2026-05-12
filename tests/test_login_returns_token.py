from fastapi import FastAPI
from httpx import AsyncClient, ASGITransport
from dependencies import get_admin_user
from models.users import User

"""Test to verify that the login endpoint returns a valid access token
for a mock user."""

async def test_login_returns_token(app: FastAPI, create_mock_user):
    user = await create_mock_user()

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
    assert "access_token" in data
    assert data["token_type"] == "bearer"