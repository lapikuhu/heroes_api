from models.users import User
from services import auth
from db import AsyncSession, get_session
from security import oauth2_scheme
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

def get_admin_user(current_user: CurrentUser) -> User:
    """Get the current authenticated admin user.
    Args:
        current_user (User): The current authenticated user.
    Returns:
        User: The authenticated admin user.
    Raises:
        HTTPException: If the user is not an admin."""
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Admin access required")
    return current_user

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
