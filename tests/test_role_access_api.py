from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient


async def _create_hero_and_mission(app: FastAPI, token: str) -> tuple[int, int]:
    async with AsyncClient(
        base_url="http://testserver",
        transport=ASGITransport(app=app),
        headers={"Authorization": f"Bearer {token}"},
    ) as client:
        hero_response = await client.post(
            "/heroes/",
            json={"name": "Role Hero", "power": "Authorization", "age": 31},
        )
        assert hero_response.status_code == 201
        hero_id = hero_response.json()["id"]

        mission_response = await client.post(
            "/missions/",
            json={
                "name": "Role Mission",
                "difficulty": 5,
                "completed": False,
                "hero_id": hero_id,
            },
        )
        assert mission_response.status_code == 201
        mission_id = mission_response.json()["id"]

    return hero_id, mission_id


async def test_viewer_can_read_heroes_and_missions(app: FastAPI, auth_mock_user):
    editor = await auth_mock_user(username="readereditor", roles=["editor"])
    hero_id, mission_id = await _create_hero_and_mission(app, editor["access_token"])
    viewer = await auth_mock_user(username="readonlyviewer", roles=["viewer"])

    async with AsyncClient(
        base_url="http://testserver",
        transport=ASGITransport(app=app),
        headers={"Authorization": f"Bearer {viewer['access_token']}"},
    ) as client:
        heroes_response = await client.get("/heroes/")
        hero_response = await client.get(f"/heroes/{hero_id}")
        missions_response = await client.get("/missions/")
        mission_response = await client.get(f"/missions/{mission_id}")

    assert heroes_response.status_code == 200
    assert hero_response.status_code == 200
    assert missions_response.status_code == 200
    assert mission_response.status_code == 200


async def test_viewer_cannot_write_content_or_access_users(app: FastAPI, auth_mock_user):
    editor = await auth_mock_user(username="writeeditor", roles=["editor"])
    hero_id, mission_id = await _create_hero_and_mission(app, editor["access_token"])
    viewer = await auth_mock_user(username="blockedviewer", roles=["viewer"])

    async with AsyncClient(
        base_url="http://testserver",
        transport=ASGITransport(app=app),
        headers={"Authorization": f"Bearer {viewer['access_token']}"},
    ) as client:
        responses = [
            await client.post("/heroes/", json={"name": "Nope", "power": "Nope", "age": 20}),
            await client.patch(f"/heroes/{hero_id}", json={"power": "Nope"}),
            await client.delete(f"/heroes/{hero_id}"),
            await client.post(
                "/missions/",
                json={"name": "Nope Mission", "difficulty": 1, "completed": False, "hero_id": hero_id},
            ),
            await client.patch(f"/missions/{mission_id}", json={"completed": True}),
            await client.delete(f"/missions/{mission_id}"),
            await client.get("/users/"),
            await client.get("/users/blockedviewer"),
            await client.post(
                "/users/register",
                json={"username": "blockedcreate", "password": "password123", "roles": ["viewer"]},
            ),
        ]
        me_response = await client.get("/users/me")

    assert all(response.status_code == 403 for response in responses)
    assert me_response.status_code == 200


async def test_editor_can_write_content_but_cannot_manage_users_or_delete(app: FastAPI, auth_mock_user):
    editor = await auth_mock_user(username="contenteditor", roles=["editor"])
    token = editor["access_token"]
    hero_id, mission_id = await _create_hero_and_mission(app, token)

    async with AsyncClient(
        base_url="http://testserver",
        transport=ASGITransport(app=app),
        headers={"Authorization": f"Bearer {token}"},
    ) as client:
        update_hero_response = await client.patch(f"/heroes/{hero_id}", json={"power": "Updated"})
        update_mission_response = await client.patch(f"/missions/{mission_id}", json={"completed": True})
        forbidden_responses = [
            await client.delete(f"/heroes/{hero_id}"),
            await client.delete(f"/missions/{mission_id}"),
            await client.get("/users/"),
            await client.post(
                "/users/register",
                json={"username": "editorcreate", "password": "password123", "roles": ["viewer"]},
            ),
        ]

    assert update_hero_response.status_code == 200
    assert update_mission_response.status_code == 200
    assert all(response.status_code == 403 for response in forbidden_responses)


async def test_is_admin_user_has_all_content_privileges_without_role_names(app: FastAPI, auth_mock_user):
    admin = await auth_mock_user(username="flagadmin", is_admin=True)
    token = admin["access_token"]

    async with AsyncClient(
        base_url="http://testserver",
        transport=ASGITransport(app=app),
        headers={"Authorization": f"Bearer {token}"},
    ) as client:
        create_hero_response = await client.post(
            "/heroes/",
            json={"name": "Flag Admin Hero", "power": "Everything", "age": 44},
        )
        assert create_hero_response.status_code == 201
        hero_id = create_hero_response.json()["id"]

        create_mission_response = await client.post(
            "/missions/",
            json={
                "name": "Flag Admin Mission",
                "difficulty": 6,
                "completed": False,
                "hero_id": hero_id,
            },
        )
        assert create_mission_response.status_code == 201
        mission_id = create_mission_response.json()["id"]

        responses = [
            await client.get("/heroes/"),
            await client.get(f"/heroes/{hero_id}"),
            await client.patch(f"/heroes/{hero_id}", json={"power": "Still Everything"}),
            await client.get("/missions/"),
            await client.get(f"/missions/{mission_id}"),
            await client.patch(f"/missions/{mission_id}", json={"completed": True}),
            await client.get("/users/"),
            await client.delete(f"/missions/{mission_id}"),
            await client.delete(f"/heroes/{hero_id}"),
        ]

    assert all(response.status_code in {200, 204} for response in responses)
