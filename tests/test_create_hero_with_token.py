from fastapi import FastAPI
from httpx import AsyncClient, ASGITransport



# Attempt to create a hero with the token -> assert 201 Created and correct response body
async def test_create_hero_with_token(app: FastAPI, auth_mock_user):
    auth_user = await auth_mock_user()
    token = auth_user["access_token"]
    async with AsyncClient(
        base_url="http://testserver",
        transport=ASGITransport(app=app),
        headers={"Authorization": f"Bearer {token}"},
    ) as client:
        response = await client.post(
            "/heroes/",
            json={
                "name": "Test Hero",
                "power": "Testing",
                "age": 30
            }
        )
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Test Hero"
        assert data["power"] == "Testing"
        assert data["age"] == 30