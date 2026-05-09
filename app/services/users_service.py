### ----------------------------- USER SERVICES------------------------- ###
# Business logic for user operations. Services are called by routes and 
# call repositories to interact with the database.
from models.users import User
from repositories import users_repo
from schemas.users import UserCreate
from security import hash_password
from sqlmodel import Session


def create_user_service(user_data: UserCreate, session: Session) -> User:
    if users_repo.is_existing_user(user_data.username, session):
        raise ValueError("Username already exists")

    user = User(
        username=user_data.username,
        hashed_password=hash_password(user_data.password),
        is_admin=user_data.is_admin,
    )
    return users_repo.create_user(user, session)

def get_user_by_username_service(username: str, session: Session) -> User | None:
    return users_repo.get_user_by_username(username, session)

def get_user_by_id_service(user_id: int, session: Session) -> User | None:
    return users_repo.get_user_by_id(user_id, session)

def get_user_roles_by_id_service(user_id: int, session: Session) -> list[str] | None:
    return users_repo.get_user_roles_by_id(user_id, session)
