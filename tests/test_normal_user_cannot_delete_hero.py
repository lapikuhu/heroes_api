from fastapi import FastAPI
from httpx import AsyncClient, ASGITransport

"""Test to verify that a normal user cannot delete a hero and receives a
403 Forbidden response when attempting to do so."""

async def test_normal_user_cannot_delete_hero(app: FastAPI, auth_mock_user, ):
    auth_user = await auth_mock_user()
    token = auth_user["access_token"]
    async with AsyncClient(
        base_url="http://testserver",
        transport=ASGITransport(app=app),
        headers={"Authorization": f"Bearer {token}"},
    ) as client:
        # First create a hero to ensure there's something to delete
        create_response = await client.post(
            "/heroes/",
            json={
                "name": "Test Hero",
                "power": "Testing",
                "age": 30
            }
        )
        assert create_response.status_code == 201
        hero_id = create_response.json()["id"]

        # Now attempt to delete the hero
        delete_response = await client.delete(f"/heroes/{hero_id}")
        assert delete_response.status_code == 403  # Forbidden for normal users
