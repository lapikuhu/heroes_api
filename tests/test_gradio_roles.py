from gradio_app.roles import can_edit_content, dashboard_for_user, is_admin


def test_admin_role_gets_admin_dashboard():
    user = {"is_admin": False, "roles": ["admin"]}

    assert is_admin(user)
    assert dashboard_for_user(user) == "admin"
    assert can_edit_content(user)


def test_is_admin_flag_gets_admin_dashboard():
    user = {"is_admin": True, "roles": ["viewer"]}

    assert is_admin(user)
    assert dashboard_for_user(user) == "admin"
    assert can_edit_content(user)


def test_editor_without_admin_gets_editor_dashboard():
    user = {"is_admin": False, "roles": ["viewer", "editor"]}

    assert not is_admin(user)
    assert dashboard_for_user(user) == "editor"
    assert can_edit_content(user)


def test_viewer_only_gets_viewer_dashboard():
    user = {"is_admin": False, "roles": ["viewer"]}

    assert not is_admin(user)
    assert dashboard_for_user(user) == "viewer"
    assert not can_edit_content(user)

