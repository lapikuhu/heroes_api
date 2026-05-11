from fastapi import FastAPI
from httpx import AsyncClient, ASGITransport

async def test_register_user(app: FastAPI):
    async with AsyncClient(
        base_url="http://testserver",
        transport=ASGITransport(app=app),
    ) as client:
        response = await client.post(
            "/users/register",
            json={
                "username": "bbbtecstu545ser34gf3",
                "email": "testuser@example.com",
                "password": "password1323"
            }
        )
        print(response.json())  # add before the assert

        assert response.status_code == 201
        data = response.json()
        assert data["ok"] is True
        assert "id" in data["user"]
        assert data["user"]["username"] == "bbbtecstu545ser34gf3"
