"""Role helpers for choosing the Gradio dashboard."""

from typing import Any


def role_names(user: dict[str, Any] | None) -> set[str]:
    """Return normalized role names for an API user payload."""
    if not user:
        return set()
    return {str(role).lower() for role in user.get("roles", [])}


def is_admin(user: dict[str, Any] | None) -> bool:
    """Return whether the user should receive the admin dashboard."""
    return bool(user and (user.get("is_admin") or "admin" in role_names(user)))


def dashboard_for_user(user: dict[str, Any] | None) -> str:
    """Return the Gradio dashboard key for an authenticated user."""
    if is_admin(user):
        return "admin"
    if "editor" in role_names(user):
        return "editor"
    return "viewer"


def can_edit_content(user: dict[str, Any] | None) -> bool:
    """Return whether the user may create or update heroes and missions."""
    return is_admin(user) or "editor" in role_names(user)

