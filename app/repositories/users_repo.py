
from models.users import User
from sqlmodel import select

from db import AsyncSession

async def create_user(user: User, session: AsyncSession) -> User:
    try:
        session.add(user)
        await session.commit()
        await session.refresh(user, attribute_names=["roles"])  # ← load roles eagerly
        return user
    except Exception:
        await session.rollback()
        raise

async def update_user(user: User, session: AsyncSession) -> User:
    try:
        session.add(user)
        await session.commit()
        await session.refresh(user, attribute_names=["roles"])  # ← load roles eagerly
        return user
    except Exception:
        await session.rollback()
        raise

async def delete_user(user: User, session: AsyncSession) -> None:
    try:
        session.delete(user)
        await session.commit()
    except Exception:
        await session.rollback()
        raise

async def get_user_by_token(token: str, session: AsyncSession) -> User | None:
    # Repo get user by token
    result = await session.exec(select(User).where(User.token == token))
    return result.first()

async def get_user_by_username(username: str, session: AsyncSession) -> User | None:
    # Repo get user by username
    result = await session.exec(select(User).where(User.username == username))
    return result.first()

async def get_user_by_id(user_id: int, session: AsyncSession) -> User | None:
    return await session.get(User, user_id)

async def is_existing_user(username: str, session: AsyncSession) -> bool:
    result = await session.exec(select(User).where(User.username == username))
    return result.first() is not None  

async def get_user_roles_by_id(user_id: int, session: AsyncSession) -> list[str] | None:
    user = await session.get(User, user_id)
    if user is None:
        return None
    return [role.name for role in user.roles]

async def is_user_admin(user_id: int, session: AsyncSession) -> bool | None:
    user = await session.get(User, user_id)
    return user.is_admin if user else None