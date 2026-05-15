from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient


async def test_update_hero_partial_can_change_power(app: FastAPI, auth_mock_user):
    auth_user = await auth_mock_user(roles=["editor"])
    token = auth_user["access_token"]

    async with AsyncClient(
        base_url="http://testserver",
        transport=ASGITransport(app=app),
        headers={"Authorization": f"Bearer {token}"},
    ) as client:
        create_response = await client.post(
            "/heroes/",
            json={
                "name": "Patch Hero",
                "power": "Flight",
                "age": 28,
            },
        )
        assert create_response.status_code == 201
        hero_id = create_response.json()["id"]

        update_response = await client.patch(
            f"/heroes/{hero_id}",
            json={
                "power": "Telepathy",
            },
        )

    assert update_response.status_code == 200
    data = update_response.json()
    assert data["name"] == "Patch Hero"
    assert data["power"] == "Telepathy"
    assert data["age"] == 28
