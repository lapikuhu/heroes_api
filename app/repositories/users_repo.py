
from click.core import F

from models.users import User
from sqlmodel import Session, select


def create_user(user: User, session: Session) -> User:
    try:
        session.add(user)
        session.commit()
        session.refresh(user)
        return user
    except Exception:
        session.rollback()
        raise

def get_user_by_token(token: str, session: Session) -> User | None:
    # Repo get user by token
    return session.exec(select(User).where(User.token == token)).first()

def get_user_by_username(username: str, session: Session) -> User | None:
    # Repo get user by username
    return session.exec(select(User).where(User.username == username)).first()

def get_user_by_id(user_id: int, session: Session) -> User | None:
    return session.get(User, user_id)

def is_existing_user(username: str, session: Session) -> bool:
    return session.exec(select(User).where(User.username == username)).first() is not None  

def get_user_roles_by_id(user_id: int, session: Session) -> list[str] | None:
    user = session.get(User, user_id)
    if user is None:
        return None
    return [role.name for role in user.roles]

def is_user_admin(user_id: int, session: Session) -> bool | None:
    user = session.get(User, user_id)
    return user.is_admin if user else None