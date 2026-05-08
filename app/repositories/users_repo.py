
from models import User
from sqlmodel import Session, select
from security import hash_password
from dependencies import SessionDep

def create_user(user: User, session: SessionDep) -> User:
    try:
        session.add(user)
        session.commit()
        session.refresh(user)
        return user
    except Exception:
        session.rollback()
        raise

def get_user_by_token(token: str, session: SessionDep) -> User | None:
    # Repo get user by token
    return session.exec(select(User).where(User.token == token)).first()

def get_user_by_username(username: str, session: SessionDep) -> User | None:
    # Repo get user by username
    return session.exec(select(User).where(User.username == username)).first()

def get_user_by_id(user_id: int, session: SessionDep) -> User | None:
    return session.get(User, user_id)

def is_existing_user(username: str, session: SessionDep) -> bool:
    return session.exec(select(User).where(User.username == username)).first() is not None  

def get_user_roles_by_id(user_id: int, session: SessionDep) -> list[str] | None:
    user = session.get(User, user_id)
    if user is None:
        return None
    return [role.name for role in user.roles]

