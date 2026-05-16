"""Standalone Gradio frontend for the Heroes API."""

from __future__ import annotations

from typing import Any

import gradio as gr

try:
    from . import api_client as api
    from .roles import dashboard_for_user
except ImportError:
    import api_client as api
    from roles import dashboard_for_user


ROLE_OPTIONS = ["admin", "editor", "viewer"]

APP_CSS = """
.login-panel {
    max-width: 460px;
    margin: 32px auto 24px;
}

.resource-section {
    margin-bottom: 18px;
    box-shadow: 0 18px 0 #bfbfbf;
}

.dashboard-panel {
    padding: 16px;
    border-radius: 10px;
}

.action-section {
    margin-top: 18px;
    padding: 16px;
    border: none;
    border-radius: 10px;
    background: var(--block-background-fill);
    box-shadow: 0 -18px 0 var(--block-background-fill);
}

.action-section > .styler,
.action-section > .block {
    border: none !important;
    box-shadow: none !important;
}

.action-section h3 {
    margin-top: 0;
    margin-bottom: 12px;
}

.danger-section {
    background: var(--block-background-fill);
    border: none;
}
"""


def _safe_int(value: Any) -> int | None:
    if value in (None, ""):
        return None
    return int(value)


def _hero_payload(name: str, power: str, age: Any) -> dict[str, Any]:
    return {"name": name, "power": power, "age": _safe_int(age)}


def _mission_payload(name: str, difficulty: Any, completed: bool, hero_id: Any) -> dict[str, Any]:
    return {
        "name": name,
        "difficulty": int(difficulty),
        "completed": bool(completed),
        "hero_id": _safe_int(hero_id),
    }


def _user_payload(username: str, password: str, is_admin: bool, roles: list[str] | None) -> dict[str, Any]:
    next_roles = roles or []
    return {
        "username": username,
        "password": password,
        "is_admin": bool(is_admin),
        "roles": next_roles,
    }


def _user_update_payload(username: str, is_admin: bool, roles: list[str] | None) -> dict[str, Any]:
    next_roles = roles or []
    return {
        "username": username,
        "is_admin": bool(is_admin),
        "roles": next_roles,
    }


def _hero_rows(heroes: list[dict[str, Any]]) -> list[list[Any]]:
    return [
        [
            hero.get("id"),
            hero.get("name"),
            hero.get("power"),
            hero.get("age"),
            ", ".join(str(value) for value in hero.get("mission_ids", [])) or "None",
        ]
        for hero in heroes
    ]


def _mission_rows(missions: list[dict[str, Any]]) -> list[list[Any]]:
    return [
        [
            mission.get("id"),
            mission.get("name"),
            mission.get("difficulty"),
            "Yes" if mission.get("completed") else "No",
            mission.get("hero_id") or "Unassigned",
        ]
        for mission in missions
    ]


def _user_rows(users: list[dict[str, Any]]) -> list[list[Any]]:
    return [
        [
            user.get("id"),
            user.get("username"),
            "Yes" if user.get("is_admin") else "No",
            ", ".join(user.get("roles", [])) or "None",
        ]
        for user in users
    ]


def _hero_choices(heroes: list[dict[str, Any]]) -> list[tuple[str, str]]:
    return [("Unassigned", "")] + [
        (f"{hero.get('id')} - {hero.get('name')}", str(hero.get("id"))) for hero in heroes
    ]


def load_heroes(base_url: str, token: str) -> list[list[Any]]:
    return _hero_rows(api.list_heroes(base_url, token))


def load_missions(base_url: str, token: str) -> tuple[list[list[Any]], gr.Dropdown]:
    heroes = api.list_heroes(base_url, token)
    missions = api.list_missions(base_url, token)
    return _mission_rows(missions), gr.update(choices=_hero_choices(heroes))


def load_users(base_url: str, token: str) -> list[list[Any]]:
    return _user_rows(api.list_users(base_url, token))


def _empty_dashboard_data() -> tuple[Any, ...]:
    empty_hero_choices = gr.update(choices=_hero_choices([]))
    return (
        [],
        [],
        empty_hero_choices,
        [],
        [],
        empty_hero_choices,
        empty_hero_choices,
        [],
        [],
        [],
        empty_hero_choices,
        empty_hero_choices,
    )


def _initial_dashboard_data(base_url: str, token: str, dashboard: str) -> tuple[Any, ...]:
    heroes = api.list_heroes(base_url, token)
    missions = api.list_missions(base_url, token)
    hero_rows = _hero_rows(heroes)
    mission_rows = _mission_rows(missions)
    hero_choices = gr.update(choices=_hero_choices(heroes))

    viewer_data = (hero_rows if dashboard == "viewer" else [], mission_rows if dashboard == "viewer" else [], hero_choices)
    editor_data = (
        hero_rows if dashboard == "editor" else [],
        mission_rows if dashboard == "editor" else [],
        hero_choices,
        hero_choices,
    )
    admin_data = (
        _user_rows(api.list_users(base_url, token)) if dashboard == "admin" else [],
        hero_rows if dashboard == "admin" else [],
        mission_rows if dashboard == "admin" else [],
        hero_choices,
        hero_choices,
    )
    return (*viewer_data, *editor_data, *admin_data)


def login_user(base_url: str, username: str, password: str) -> tuple[Any, ...]:
    try:
        token = api.login(base_url, username, password)["access_token"]
        user = api.me(base_url, token)
        dashboard = dashboard_for_user(user)
        status = f"Signed in as {user['username']} ({dashboard})"
    except api.ApiError as exc:
        return (
            None,
            None,
            gr.update(visible=True),
            gr.update(visible=False),
            gr.update(visible=False),
            gr.update(visible=False),
            gr.update(visible=False),
            str(exc),
            *_empty_dashboard_data(),
        )

    initial_data = _initial_dashboard_data(base_url, token, dashboard)
    return (
        token,
        user,
        gr.update(visible=False),
        gr.update(visible=dashboard == "viewer"),
        gr.update(visible=dashboard == "editor"),
        gr.update(visible=dashboard == "admin"),
        gr.update(visible=True),
        status,
        *initial_data,
    )


def logout_user() -> tuple[Any, ...]:
    return (
        None,
        None,
        gr.update(visible=True),
        gr.update(visible=False),
        gr.update(visible=False),
        gr.update(visible=False),
        gr.update(visible=False),
        "Signed out.",
    )


def create_hero(base_url: str, token: str, name: str, power: str, age: Any) -> tuple[list[list[Any]], str]:
    try:
        api.create_hero(base_url, token, _hero_payload(name, power, age))
        return load_heroes(base_url, token), "Hero created."
    except (api.ApiError, ValueError) as exc:
        return load_heroes(base_url, token), str(exc)


def update_hero(base_url: str, token: str, hero_id: Any, name: str, power: str, age: Any) -> tuple[list[list[Any]], str]:
    try:
        api.update_hero(base_url, token, int(hero_id), _hero_payload(name, power, age))
        return load_heroes(base_url, token), "Hero updated."
    except (api.ApiError, ValueError) as exc:
        return load_heroes(base_url, token), str(exc)


def delete_hero(base_url: str, token: str, hero_id: Any) -> tuple[list[list[Any]], str]:
    try:
        api.delete_hero(base_url, token, int(hero_id))
        return load_heroes(base_url, token), "Hero deleted."
    except (api.ApiError, ValueError) as exc:
        return load_heroes(base_url, token), str(exc)


def create_mission(
    base_url: str,
    token: str,
    name: str,
    difficulty: Any,
    completed: bool,
    hero_id: Any,
) -> tuple[list[list[Any]], str]:
    try:
        api.create_mission(base_url, token, _mission_payload(name, difficulty, completed, hero_id))
        rows, _ = load_missions(base_url, token)
        return rows, "Mission created."
    except (api.ApiError, ValueError) as exc:
        rows, _ = load_missions(base_url, token)
        return rows, str(exc)


def update_mission(
    base_url: str,
    token: str,
    mission_id: Any,
    name: str,
    difficulty: Any,
    completed: bool,
    hero_id: Any,
) -> tuple[list[list[Any]], str]:
    try:
        api.update_mission(base_url, token, int(mission_id), _mission_payload(name, difficulty, completed, hero_id))
        rows, _ = load_missions(base_url, token)
        return rows, "Mission updated."
    except (api.ApiError, ValueError) as exc:
        rows, _ = load_missions(base_url, token)
        return rows, str(exc)


def delete_mission(base_url: str, token: str, mission_id: Any) -> tuple[list[list[Any]], str]:
    try:
        api.delete_mission(base_url, token, int(mission_id))
        rows, _ = load_missions(base_url, token)
        return rows, "Mission deleted."
    except (api.ApiError, ValueError) as exc:
        rows, _ = load_missions(base_url, token)
        return rows, str(exc)


def create_user(
    base_url: str,
    token: str,
    username: str,
    password: str,
    is_admin: bool,
    roles: list[str] | None,
) -> tuple[list[list[Any]], str]:
    try:
        api.create_user(base_url, token, _user_payload(username, password, is_admin, roles))
        return load_users(base_url, token), "User created."
    except api.ApiError as exc:
        return load_users(base_url, token), str(exc)


def update_user(
    base_url: str,
    token: str,
    user_id: Any,
    username: str,
    is_admin: bool,
    roles: list[str] | None,
) -> tuple[list[list[Any]], str]:
    try:
        api.update_user(base_url, token, int(user_id), _user_update_payload(username, is_admin, roles))
        return load_users(base_url, token), "User updated."
    except (api.ApiError, ValueError) as exc:
        return load_users(base_url, token), str(exc)


def delete_user(base_url: str, token: str, current_user: dict[str, Any], user_id: Any) -> tuple[list[list[Any]], str]:
    try:
        target_id = int(user_id)
        if target_id == current_user.get("id"):
            return load_users(base_url, token), "You cannot delete your own signed-in account from this UI."
        api.delete_user(base_url, token, target_id)
        return load_users(base_url, token), "User deleted."
    except (api.ApiError, ValueError) as exc:
        return load_users(base_url, token), str(exc)


def build_app() -> gr.Blocks:
    with gr.Blocks(title="Heroes API Gradio Admin", css=APP_CSS) as demo:
        token_state = gr.State(None)
        user_state = gr.State(None)

        gr.Markdown("# Heroes API")
        status = gr.Markdown("Sign in to open your role-based dashboard.")

        with gr.Group(elem_classes="login-panel") as login_panel:
            api_base_url = gr.Textbox(label="API base URL", value=api.DEFAULT_API_BASE_URL)
            username = gr.Textbox(label="Username")
            password = gr.Textbox(label="Password", type="password")
            login_button = gr.Button("Sign in", variant="primary")

        with gr.Row(visible=False) as session_bar:
            logout_button = gr.Button("Sign out")

        hero_headers = ["ID", "Name", "Power", "Age", "Mission IDs"]
        mission_headers = ["ID", "Name", "Difficulty", "Completed", "Hero ID"]
        user_headers = ["ID", "Username", "Admin", "Roles"]

        with gr.Group(visible=False, elem_classes="dashboard-panel") as viewer_dashboard:
            gr.Markdown("## Viewer Dashboard")
            with gr.Tabs():
                with gr.Tab("Heroes"):
                    with gr.Group(elem_classes="resource-section"):
                        viewer_heroes = gr.Dataframe(headers=hero_headers, interactive=False)
                        viewer_refresh_heroes = gr.Button("Refresh heroes")
                with gr.Tab("Missions"):
                    with gr.Group(elem_classes="resource-section"):
                        viewer_missions = gr.Dataframe(headers=mission_headers, interactive=False)
                        viewer_mission_hero_id = gr.Dropdown(label="Assigned hero", visible=False)
                        viewer_refresh_missions = gr.Button("Refresh missions")

        with gr.Group(visible=False, elem_classes="dashboard-panel") as editor_dashboard:
            gr.Markdown("## Editor Dashboard")
            with gr.Tabs():
                with gr.Tab("Heroes"):
                    with gr.Group(elem_classes="resource-section"):
                        editor_heroes = gr.Dataframe(headers=hero_headers, interactive=False)
                        editor_refresh_heroes = gr.Button("Refresh heroes")
                    with gr.Group(elem_classes="action-section"):
                        gr.Markdown("### Create hero")
                        with gr.Row():
                            hero_name = gr.Textbox(label="New hero name")
                            hero_power = gr.Textbox(label="Power")
                            hero_age = gr.Number(label="Age", precision=0)
                        editor_create_hero = gr.Button("Create hero", variant="primary")
                    with gr.Group(elem_classes="action-section"):
                        gr.Markdown("### Update hero")
                        with gr.Row():
                            edit_hero_id = gr.Number(label="Hero ID", precision=0)
                            edit_hero_name = gr.Textbox(label="Name")
                            edit_hero_power = gr.Textbox(label="Power")
                            edit_hero_age = gr.Number(label="Age", precision=0)
                        editor_update_hero = gr.Button("Update hero")
                with gr.Tab("Missions"):
                    with gr.Group(elem_classes="resource-section"):
                        editor_missions = gr.Dataframe(headers=mission_headers, interactive=False)
                        editor_refresh_missions = gr.Button("Refresh missions")
                    with gr.Group(elem_classes="action-section"):
                        gr.Markdown("### Create mission")
                        editor_mission_hero_id = gr.Dropdown(label="Assigned hero")
                        with gr.Row():
                            mission_name = gr.Textbox(label="New mission name")
                            mission_difficulty = gr.Number(label="Difficulty", value=1, precision=0)
                            mission_completed = gr.Checkbox(label="Completed")
                        editor_create_mission = gr.Button("Create mission", variant="primary")
                    with gr.Group(elem_classes="action-section"):
                        gr.Markdown("### Update mission")
                        with gr.Row():
                            edit_mission_id = gr.Number(label="Mission ID", precision=0)
                            edit_mission_name = gr.Textbox(label="Name")
                            edit_mission_difficulty = gr.Number(label="Difficulty", value=1, precision=0)
                            edit_mission_completed = gr.Checkbox(label="Completed")
                            edit_mission_hero_id = gr.Dropdown(label="Assigned hero")
                        editor_update_mission = gr.Button("Update mission")

        with gr.Group(visible=False, elem_classes="dashboard-panel") as admin_dashboard:
            gr.Markdown("## Admin Dashboard")
            with gr.Tabs():
                with gr.Tab("Users"):
                    with gr.Group(elem_classes="resource-section"):
                        admin_users = gr.Dataframe(headers=user_headers, interactive=False)
                        admin_refresh_users = gr.Button("Refresh users")
                    with gr.Group(elem_classes="action-section"):
                        gr.Markdown("### Create user")
                        with gr.Row():
                            new_username = gr.Textbox(label="Username")
                            new_password = gr.Textbox(label="Password", type="password")
                            new_is_admin = gr.Checkbox(label="Admin")
                            new_roles = gr.CheckboxGroup(label="Roles", choices=ROLE_OPTIONS, value=["viewer"])
                        admin_create_user = gr.Button("Create user", variant="primary")
                    with gr.Group(elem_classes="action-section"):
                        gr.Markdown("### Update user")
                        with gr.Row():
                            edit_user_id = gr.Number(label="User ID", precision=0)
                            edit_username = gr.Textbox(label="Username")
                            edit_is_admin = gr.Checkbox(label="Admin")
                            edit_roles = gr.CheckboxGroup(label="Roles", choices=ROLE_OPTIONS)
                        admin_update_user = gr.Button("Update user")
                    with gr.Group(elem_classes=["action-section", "danger-section"]):
                        gr.Markdown("### Delete user")
                        delete_user_id = gr.Number(label="User ID to delete", precision=0)
                        admin_delete_user = gr.Button("Delete user", variant="stop")
                with gr.Tab("Heroes"):
                    with gr.Group(elem_classes="resource-section"):
                        admin_heroes = gr.Dataframe(headers=hero_headers, interactive=False)
                        admin_refresh_heroes = gr.Button("Refresh heroes")
                    with gr.Group(elem_classes="action-section"):
                        gr.Markdown("### Create hero")
                        with gr.Row():
                            admin_hero_name = gr.Textbox(label="New hero name")
                            admin_hero_power = gr.Textbox(label="Power")
                            admin_hero_age = gr.Number(label="Age", precision=0)
                        admin_create_hero = gr.Button("Create hero", variant="primary")
                    with gr.Group(elem_classes="action-section"):
                        gr.Markdown("### Update hero")
                        with gr.Row():
                            admin_edit_hero_id = gr.Number(label="Hero ID", precision=0)
                            admin_edit_hero_name = gr.Textbox(label="Name")
                            admin_edit_hero_power = gr.Textbox(label="Power")
                            admin_edit_hero_age = gr.Number(label="Age", precision=0)
                        admin_update_hero = gr.Button("Update hero")
                    with gr.Group(elem_classes=["action-section", "danger-section"]):
                        gr.Markdown("### Delete hero")
                        admin_delete_hero_id = gr.Number(label="Hero ID to delete", precision=0)
                        admin_delete_hero = gr.Button("Delete hero", variant="stop")
                with gr.Tab("Missions"):
                    with gr.Group(elem_classes="resource-section"):
                        admin_missions = gr.Dataframe(headers=mission_headers, interactive=False)
                        admin_refresh_missions = gr.Button("Refresh missions")
                    with gr.Group(elem_classes="action-section"):
                        gr.Markdown("### Create mission")
                        admin_mission_hero_id = gr.Dropdown(label="Assigned hero")
                        with gr.Row():
                            admin_mission_name = gr.Textbox(label="New mission name")
                            admin_mission_difficulty = gr.Number(label="Difficulty", value=1, precision=0)
                            admin_mission_completed = gr.Checkbox(label="Completed")
                        admin_create_mission = gr.Button("Create mission", variant="primary")
                    with gr.Group(elem_classes="action-section"):
                        gr.Markdown("### Update mission")
                        with gr.Row():
                            admin_edit_mission_id = gr.Number(label="Mission ID", precision=0)
                            admin_edit_mission_name = gr.Textbox(label="Name")
                            admin_edit_mission_difficulty = gr.Number(label="Difficulty", value=1, precision=0)
                            admin_edit_mission_completed = gr.Checkbox(label="Completed")
                            admin_edit_mission_hero_id = gr.Dropdown(label="Assigned hero")
                        admin_update_mission = gr.Button("Update mission")
                    with gr.Group(elem_classes=["action-section", "danger-section"]):
                        gr.Markdown("### Delete mission")
                        admin_delete_mission_id = gr.Number(label="Mission ID to delete", precision=0)
                        admin_delete_mission = gr.Button("Delete mission", variant="stop")

        login_button.click(
            login_user,
            inputs=[api_base_url, username, password],
            outputs=[
                token_state,
                user_state,
                login_panel,
                viewer_dashboard,
                editor_dashboard,
                admin_dashboard,
                session_bar,
                status,
                viewer_heroes,
                viewer_missions,
                viewer_mission_hero_id,
                editor_heroes,
                editor_missions,
                editor_mission_hero_id,
                edit_mission_hero_id,
                admin_users,
                admin_heroes,
                admin_missions,
                admin_mission_hero_id,
                admin_edit_mission_hero_id,
            ],
        )
        logout_button.click(
            logout_user,
            outputs=[
                token_state,
                user_state,
                login_panel,
                viewer_dashboard,
                editor_dashboard,
                admin_dashboard,
                session_bar,
                status,
            ],
        )

        viewer_refresh_heroes.click(load_heroes, inputs=[api_base_url, token_state], outputs=[viewer_heroes])
        viewer_refresh_missions.click(
            load_missions,
            inputs=[api_base_url, token_state],
            outputs=[viewer_missions, viewer_mission_hero_id],
        )

        editor_refresh_heroes.click(load_heroes, inputs=[api_base_url, token_state], outputs=[editor_heroes])
        editor_create_hero.click(
            create_hero,
            inputs=[api_base_url, token_state, hero_name, hero_power, hero_age],
            outputs=[editor_heroes, status],
        )
        editor_update_hero.click(
            update_hero,
            inputs=[api_base_url, token_state, edit_hero_id, edit_hero_name, edit_hero_power, edit_hero_age],
            outputs=[editor_heroes, status],
        )
        editor_refresh_missions.click(
            load_missions,
            inputs=[api_base_url, token_state],
            outputs=[editor_missions, editor_mission_hero_id],
        )
        editor_create_mission.click(
            create_mission,
            inputs=[api_base_url, token_state, mission_name, mission_difficulty, mission_completed, editor_mission_hero_id],
            outputs=[editor_missions, status],
        )
        editor_update_mission.click(
            update_mission,
            inputs=[
                api_base_url,
                token_state,
                edit_mission_id,
                edit_mission_name,
                edit_mission_difficulty,
                edit_mission_completed,
                edit_mission_hero_id,
            ],
            outputs=[editor_missions, status],
        )

        admin_refresh_users.click(load_users, inputs=[api_base_url, token_state], outputs=[admin_users])
        admin_create_user.click(
            create_user,
            inputs=[api_base_url, token_state, new_username, new_password, new_is_admin, new_roles],
            outputs=[admin_users, status],
        )
        admin_update_user.click(
            update_user,
            inputs=[api_base_url, token_state, edit_user_id, edit_username, edit_is_admin, edit_roles],
            outputs=[admin_users, status],
        )
        admin_delete_user.click(
            delete_user,
            inputs=[api_base_url, token_state, user_state, delete_user_id],
            outputs=[admin_users, status],
        )
        admin_refresh_heroes.click(load_heroes, inputs=[api_base_url, token_state], outputs=[admin_heroes])
        admin_create_hero.click(
            create_hero,
            inputs=[api_base_url, token_state, admin_hero_name, admin_hero_power, admin_hero_age],
            outputs=[admin_heroes, status],
        )
        admin_update_hero.click(
            update_hero,
            inputs=[
                api_base_url,
                token_state,
                admin_edit_hero_id,
                admin_edit_hero_name,
                admin_edit_hero_power,
                admin_edit_hero_age,
            ],
            outputs=[admin_heroes, status],
        )
        admin_delete_hero.click(
            delete_hero,
            inputs=[api_base_url, token_state, admin_delete_hero_id],
            outputs=[admin_heroes, status],
        )
        admin_refresh_missions.click(
            load_missions,
            inputs=[api_base_url, token_state],
            outputs=[admin_missions, admin_mission_hero_id],
        )
        admin_create_mission.click(
            create_mission,
            inputs=[
                api_base_url,
                token_state,
                admin_mission_name,
                admin_mission_difficulty,
                admin_mission_completed,
                admin_mission_hero_id,
            ],
            outputs=[admin_missions, status],
        )
        admin_update_mission.click(
            update_mission,
            inputs=[
                api_base_url,
                token_state,
                admin_edit_mission_id,
                admin_edit_mission_name,
                admin_edit_mission_difficulty,
                admin_edit_mission_completed,
                admin_edit_mission_hero_id,
            ],
            outputs=[admin_missions, status],
        )
        admin_delete_mission.click(
            delete_mission,
            inputs=[api_base_url, token_state, admin_delete_mission_id],
            outputs=[admin_missions, status],
        )

    return demo


demo = build_app()


if __name__ == "__main__":
    demo.launch()
