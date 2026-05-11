from fastapi import FastAPI
from httpx import AsyncClient, ASGITransport

async def test_create_mission_for_missing_hero_returns_404(app: FastAPI, auth_mock_user):
    auth_user = await auth_mock_user()
    token = auth_user["access_token"]
    async with AsyncClient(
        base_url="http://testserver",
        transport=ASGITransport(app=app),
        headers={"Authorization": f"Bearer {token}"},
    ) as client:
        response = await client.post(
            "/missions/",
            json={
                "name": "Test Mission",
                "difficulty": "7",
                "completed": "False",
                "hero_id": 9999  # Assuming this hero ID does not exist
            }
        )
        assert response.status_code == 404