### ----------------------------- USER SERVICES------------------------- ###
# Business logic for user operations. Services are called by routes and 
# call repositories to interact with the database.
from models import User
from repositories import users_repo
from schemas.users import UserCreate
from security import hash_password
from sqlmodel import Session
from fastapi import Depends, Header, HTTPException
from typing import Annotated

from dependencies import SessionDep

def get_token(x_token: Annotated[str, Header()], session: SessionDep) -> str:
    """Service function to validate the token from the request header.
    Args:
        x_token (str): The token provided in the request header.
        session (Session): The database session dependency.
    Returns:
        str: The valid token if it exists in the session.    
    """
    if x_token not in session: # .keys() -> token-alice, token-bob, token-charlie
        raise HTTPException(status_code=401, detail="Invalid token")
    return x_token

def get_current_user(token: Annotated[str, Depends(get_token)]) -> User:
    user = users_repo.get_user_by_token(token)
    if user is None:
        raise HTTPException(status_code=401, detail="Invalid token")
    return user

def create_user_service(user_data: UserCreate, session: SessionDep) -> User:
    if users_repo.is_existing_user(user_data.username, session):
        raise ValueError("Username already exists")

    user = User(
        username=user_data.username,
        hashed_password=hash_password(user_data.password),
        is_admin=user_data.is_admin,
    )
    return users_repo.create_user(user, session)

def get_user_by_username_service(username: str, session: SessionDep) -> User | None:
    return users_repo.get_user_by_username(username, session)

def get_user_by_id_service(user_id: int, session: SessionDep) -> User | None:
    return users_repo.get_user_by_id(user_id, session)

def get_user_roles_by_id_service(user_id: int, session: SessionDep) -> list[str] | None:
    return users_repo.get_user_roles_by_id(user_id, session)

def get_token(x_token: Annotated[str, Header()], session: SessionDep) -> str:
    if x_token not in session: # .keys()
        raise HTTPException(status_code=401, detail="Invalid token")
    return x_token