from models.users import User
from services import auth
from db import AsyncSession, get_session
from security import oauth2_scheme
from collections.abc import Callable
from typing import Annotated
from fastapi import Depends, HTTPException

# Dependency for getting a database session
SessionDep = Annotated[AsyncSession, Depends(get_session)]
TokenDep = Annotated[str, Depends(oauth2_scheme)]


async def get_current_user(token: TokenDep, session: SessionDep) -> User:
    """Get the current authenticated user based on the provided JWT token.
    Args:
        token (str): The JWT token extracted from the Authorization header.
        session (AsyncSession): The database session for querying user data.
    Returns:
        User: The authenticated user object.
    Raises:
        HTTPException: If the token is invalid or the user cannot be authenticated."""
    user = await auth.get_current_user(token, session)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid authentication credentials")
    return user

# Create the current user dependency for FastAPI routes
CurrentUser = Annotated[User, Depends(get_current_user)]


def get_user_role_names(user: User) -> set[str]:
    """Return the user's role names as a normalized set."""
    return {role.name for role in (getattr(user, "roles", None) or [])}


def is_admin_user(user: User) -> bool:
    """Return whether the user has admin privileges."""
    return user.is_admin or "admin" in get_user_role_names(user)


def require_roles(*allowed_roles: str) -> Callable[[User], User]:
    """Build a dependency that allows users with any of the given roles."""

    def role_dependency(current_user: CurrentUser) -> User:
        user_roles = get_user_role_names(current_user)
        if is_admin_user(current_user) or user_roles.intersection(allowed_roles):
            return current_user
        raise HTTPException(status_code=403, detail="Insufficient role permissions")

    return role_dependency


def get_viewer_user(current_user: CurrentUser) -> User:
    """Get a user who can view heroes and missions."""
    return require_roles("viewer", "editor", "admin")(current_user)


def get_editor_user(current_user: CurrentUser) -> User:
    """Get a user who can create and update heroes and missions."""
    return require_roles("editor", "admin")(current_user)


def get_admin_user(current_user: CurrentUser) -> User:
    """Get the current authenticated admin user.
    Args:
        current_user (User): The current authenticated user.
    Returns:
        User: The authenticated admin user.
    Raises:
        HTTPException: If the user is not an admin."""
    if not is_admin_user(current_user):
        raise HTTPException(status_code=403, detail="Admin access required")
    return current_user


ViewerUser = Annotated[User, Depends(get_viewer_user)]
EditorUser = Annotated[User, Depends(get_editor_user)]
AdminUser = Annotated[User, Depends(get_admin_user)]


# --- PAGINATION DEPENDENCY ---

def pagination(skip: int = 0, limit: int = 20) -> dict:
    """Reusable pagination dependency.
    Args:
        skip (int): The number of items to skip.
        limit (int): The maximum number of items to return.
    Returns:
        dict: A dictionary containing the skip and limit values."""
    return {"skip": skip, "limit": limit}


Page = Annotated[dict, Depends(pagination)]
