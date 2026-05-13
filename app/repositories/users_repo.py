
from models.users import User
from sqlalchemy.orm import selectinload
from sqlmodel import select

from db import AsyncSession

async def create_user(user: User, session: AsyncSession) -> User:
    """Create a new user in the database and return the created user with its ID.
    Args:
        user (User): The user instance to create.
        session (AsyncSession): The database session to use for the operation.
    Returns:
        User: The created user instance with its ID.
    Raises:
        Exception: If there is an error during the database operation, it will be rolled back and the exception will be propagated."""
    try:
        session.add(user)
        await session.commit()
        await session.refresh(user, attribute_names=["roles"])  # ← load roles eagerly
        return user
    except Exception:
        await session.rollback()
        raise

async def update_user(user: User, session: AsyncSession) -> User:
    """Update an existing user in the database and return the updated user.
    Args:
        user (User): The user instance with updated data. The instance must have a valid ID
        session (AsyncSession): The database session to use for the operation.
    Returns:
        User: The updated user instance.
    Raises:
        Exception: If there is an error during the database operation, it will be rolled back and the exception will be propagated.
    """
    try:
        session.add(user)
        await session.commit()
        await session.refresh(user, attribute_names=["roles"])  # ← load roles eagerly
        return user
    except Exception:
        await session.rollback()
        raise

async def delete_user(user: User, session: AsyncSession) -> None:
    """Delete a user from the database.
    Args:
        user (User): The user instance to delete.
        session (AsyncSession): The database session to use for the operation.
    Raises:
        Exception: If there is an error during the database operation, it will be rolled back and the exception will be propagated.
    """
    try:
        await session.delete(user)
        await session.commit()
    except Exception:
        await session.rollback()
        raise

async def get_user_by_token(token: str, session: AsyncSession) -> User | None:
    """Get a user by their authentication token. Returns None if the user does not exist.
    Args:
        token (str): The authentication token of the user to retrieve.
        session (AsyncSession): The database session to use for the operation.
    Returns:
        User | None: The user instance if found, otherwise None.
    """
    # Repo get user by token
    result = await session.exec(select(User).where(User.token == token))
    return result.first()

async def get_user_by_username(username: str, session: AsyncSession) -> User | None:
    """Get a user by their username. Returns None if the user does not exist.
    Args:
        username (str): The username of the user to retrieve.
        session (AsyncSession): The database session to use for the operation.
    Returns:
        User | None: The user instance if found, otherwise None.
    """
    result = await session.exec(
        select(User).options(selectinload(User.roles)).where(User.username == username)
    )
    return result.first()

async def get_user_by_id(user_id: int, session: AsyncSession) -> User | None:
    """Get a user by their ID. Returns None if the user does not exist.
    Args:
        user_id (int): The ID of the user to retrieve.
        session (AsyncSession): The database session to use for the operation.
    Returns:
        User | None: The user instance if found, otherwise None.
    """
    result = await session.exec(
        select(User).options(selectinload(User.roles)).where(User.id == user_id)
    )
    return result.first()

async def get_all_users(session: AsyncSession) -> list[User]:
    """Get a list of all users.
    Args:
        session (AsyncSession): The database session to use for the operation.
    Returns:
        list[User]: A list of all user instances.
    """
    result = await session.exec(select(User).options(selectinload(User.roles)))
    return list(result.all())

async def is_existing_user(username: str, session: AsyncSession) -> bool:
    """Check if a user with the given username already exists in the database.
    Args:
        username (str): The username of the user to check for existence.
        session (AsyncSession): The database session to use for the operation.
    Returns:
        bool: True if the user exists, False otherwise.
    """
    result = await session.exec(select(User).where(User.username == username))
    return result.first() is not None  

async def get_user_roles_by_id(user_id: int, session: AsyncSession) -> list[str] | None:
    """Get the roles of a user by their ID. Returns None if the user does not exist.
    Args:
        user_id (int): The ID of the user to retrieve roles for.
        session (AsyncSession): The database session to use for the operation.
    Returns:
        list[str] | None: A list of role names if the user exists, otherwise None.
    """
    user = await session.get(User, user_id)
    if user is None:
        return None
    return [role.name for role in user.roles]

async def is_user_admin(user_id: int, session: AsyncSession) -> bool | None:
    """Check if a user is an admin by their ID. Returns None if the user does not exist.
    Args:
        user_id (int): The ID of the user to check.
        session (AsyncSession): The database session to use for the operation.
    Returns:
        bool | None: True if the user is an admin, False if not, or None if the user does not exist.
    """
    user = await session.get(User, user_id)
    return user.is_admin if user else None
