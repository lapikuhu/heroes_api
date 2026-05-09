from sqlmodel import Session
from models.users import User
from services import auth
from db import get_session
from security import oauth2_scheme
from typing import Annotated
from fastapi import Depends

# Dependency for getting a database session
SessionDep = Annotated[Session, Depends(get_session)]
TokenDep = Annotated[str, Depends(oauth2_scheme)]


def get_current_user(token: TokenDep, session: SessionDep) -> User:
    return auth.get_current_user(token, session)

# Create the current user dependency for FastAPI routes
CurrentUser = Annotated[User, Depends(get_current_user)]
