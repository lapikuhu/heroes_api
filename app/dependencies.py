from sqlmodel import Session
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
    user = await auth.get_current_user(token, session)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid authentication credentials")
    return user

# Create the current user dependency for FastAPI routes
CurrentUser = Annotated[User, Depends(get_current_user)]

def get_admin_user(current_user: CurrentUser) -> User:
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Admin access required")
    return current_user

AdminUser = Annotated[User, Depends(get_admin_user)]
