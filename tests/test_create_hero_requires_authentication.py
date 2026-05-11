from fastapi import FastAPI
from httpx import AsyncClient, ASGITransport

# Attempt to create a hero without authentication -> assert 401 Unauthorized

async def test_create_hero_requires_authentication(app: FastAPI):
    async with AsyncClient(
        base_url="http://testserver",
        transport=ASGITransport(app=app),
    ) as client:
        response = await client.post(
            "/heroes/",
            json={
                "name": "Test Hero",
                "power": "Testing",
                "age": 30
            }
        )
        assert response.status_code == 401