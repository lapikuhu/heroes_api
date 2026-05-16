"""Small HTTP client for the existing FastAPI backend."""

from __future__ import annotations

import json
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen


DEFAULT_API_BASE_URL = "http://127.0.0.1:8000"


class ApiError(RuntimeError):
    """Raised when the FastAPI backend returns an error."""


def clean_base_url(base_url: str | None) -> str:
    """Normalize a user-provided API base URL."""
    return (base_url or DEFAULT_API_BASE_URL).strip().rstrip("/")


def request_json(
    base_url: str,
    path: str,
    *,
    method: str = "GET",
    token: str | None = None,
    payload: dict[str, Any] | None = None,
    form: dict[str, Any] | None = None,
) -> Any:
    """Send a JSON or form request to the FastAPI API."""
    headers: dict[str, str] = {}
    body: bytes | None = None

    if token:
        headers["Authorization"] = f"Bearer {token}"

    if form is not None:
        body = urlencode(form).encode("utf-8")
        headers["Content-Type"] = "application/x-www-form-urlencoded"
    elif payload is not None:
        body = json.dumps(payload).encode("utf-8")
        headers["Content-Type"] = "application/json"

    req = Request(
        f"{clean_base_url(base_url)}{path}",
        data=body,
        headers=headers,
        method=method,
    )

    try:
        with urlopen(req, timeout=10) as response:
            if response.status == 204:
                return None
            raw = response.read()
    except HTTPError as exc:
        raise ApiError(_error_detail(exc)) from exc
    except URLError as exc:
        raise ApiError(f"Could not reach API: {exc.reason}") from exc

    if not raw:
        return None
    return json.loads(raw.decode("utf-8"))


def _error_detail(exc: HTTPError) -> str:
    raw = exc.read()
    if not raw:
        return f"Request failed with {exc.code}"
    try:
        data = json.loads(raw.decode("utf-8"))
    except json.JSONDecodeError:
        return raw.decode("utf-8", errors="replace")
    return str(data.get("detail") or f"Request failed with {exc.code}")


def login(base_url: str, username: str, password: str) -> dict[str, Any]:
    return request_json(
        base_url,
        "/users/login",
        method="POST",
        form={"username": username, "password": password},
    )


def me(base_url: str, token: str) -> dict[str, Any]:
    return request_json(base_url, "/users/me", token=token)


def list_users(base_url: str, token: str) -> list[dict[str, Any]]:
    return request_json(base_url, "/users/", token=token)


def create_user(base_url: str, token: str, payload: dict[str, Any]) -> dict[str, Any]:
    return request_json(base_url, "/users/register", method="POST", token=token, payload=payload)


def update_user(base_url: str, token: str, user_id: int, payload: dict[str, Any]) -> dict[str, Any]:
    return request_json(base_url, f"/users/{user_id}", method="PATCH", token=token, payload=payload)


def delete_user(base_url: str, token: str, user_id: int) -> None:
    request_json(base_url, f"/users/{user_id}", method="DELETE", token=token)


def list_heroes(base_url: str, token: str) -> list[dict[str, Any]]:
    return request_json(base_url, "/heroes/", token=token)


def create_hero(base_url: str, token: str, payload: dict[str, Any]) -> dict[str, Any]:
    return request_json(base_url, "/heroes/", method="POST", token=token, payload=payload)


def update_hero(base_url: str, token: str, hero_id: int, payload: dict[str, Any]) -> dict[str, Any]:
    return request_json(base_url, f"/heroes/{hero_id}", method="PATCH", token=token, payload=payload)


def delete_hero(base_url: str, token: str, hero_id: int) -> None:
    request_json(base_url, f"/heroes/{hero_id}", method="DELETE", token=token)


def list_missions(base_url: str, token: str) -> list[dict[str, Any]]:
    return request_json(base_url, "/missions/", token=token)


def create_mission(base_url: str, token: str, payload: dict[str, Any]) -> dict[str, Any]:
    return request_json(base_url, "/missions/", method="POST", token=token, payload=payload)


def update_mission(base_url: str, token: str, mission_id: int, payload: dict[str, Any]) -> dict[str, Any]:
    return request_json(base_url, f"/missions/{mission_id}", method="PATCH", token=token, payload=payload)


def delete_mission(base_url: str, token: str, mission_id: int) -> None:
    request_json(base_url, f"/missions/{mission_id}", method="DELETE", token=token)

