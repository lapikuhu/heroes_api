from fastapi import FastAPI
from httpx import AsyncClient, ASGITransport

"""Test to verify that a new user can successfully register using the
 /users/register endpoint."""

# Session and mock_admin user overrides are handled by the test fixture in conftest.py
async def test_register_user(app: FastAPI, admin_override):
    async with AsyncClient(
        base_url="http://testserver",
        transport=ASGITransport(app=app),
    ) as client:
        response = await client.post(
            "/users/register",
            json={
                "username": "ffffg",
                "email": "testuser@example.com",
                "password": "password1323"
            }
        )

        assert response.status_code == 201
        data = response.json()
        assert data["ok"] is True
        assert "id" in data["user"]
        assert data["user"]["username"] == "ffffg"
