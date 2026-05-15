from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient


async def test_update_mission_can_patch_completed_only(app: FastAPI, auth_mock_user):
    auth_user = await auth_mock_user(roles=["editor"])

    async with AsyncClient(
        base_url="http://testserver",
        transport=ASGITransport(app=app),
    ) as client:
        create_hero_response = await client.post(
            "/heroes/",
            headers={"Authorization": f"Bearer {auth_user['access_token']}"},
            json={"name": "Patch Hero", "power": "Patch Power", "age": 33},
        )
        assert create_hero_response.status_code == 201

        create_mission_response = await client.post(
            "/missions/",
            headers={"Authorization": f"Bearer {auth_user['access_token']}"},
            json={
                "name": "Patch mission",
                "difficulty": 4,
                "completed": False,
                "hero_id": create_hero_response.json()["id"],
            },
        )
        assert create_mission_response.status_code == 201
        mission = create_mission_response.json()

        update_response = await client.patch(
            f"/missions/{mission['id']}",
            headers={"Authorization": f"Bearer {auth_user['access_token']}"},
            json={"completed": True},
        )

    assert update_response.status_code == 200
    data = update_response.json()
    assert data["name"] == "Patch mission"
    assert data["difficulty"] == 4
    assert data["completed"] is True
