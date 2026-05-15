from fastapi import FastAPI
from httpx import AsyncClient, ASGITransport

"""Test to verify that an admin user can successfully delete a mission.
This test creates a mission, then attempts to delete it using an admin user's credentials."""

async def test_admin_can_delete_mission(app: FastAPI, auth_mock_user, admin_override):
    auth_user = await auth_mock_user(roles=["admin"], is_admin=True)
    token = auth_user["access_token"]

    async with AsyncClient(
        base_url="http://testserver",
        transport=ASGITransport(app=app),
        headers={"Authorization": f"Bearer {token}"},
    ) as client:
        # Create dummy hero to assign the mission to
        create_hero_response = await client.post(
            "/heroes/",
            json={
                "name": "Mission Deletion Hero",
                "power": "Testing",
                "age": 40
            }
        )
        assert create_hero_response.status_code == 201
        hero_id = create_hero_response.json()["id"]
        # Create a mission to delete
        create_mission_response = await client.post(
            "/missions/",
            json={
                "name": "Test Mission",
                "difficulty": 5,
                "completed": False,
                "hero_id": hero_id
            }
        )
        assert create_mission_response.status_code == 201
        mission_id = create_mission_response.json()["id"]
        # Delete the mission
        delete_mission_response = await client.delete(f"/missions/{mission_id}")
        assert delete_mission_response.status_code == 204
