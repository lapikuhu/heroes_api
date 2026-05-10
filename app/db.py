from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from models import user_roles
from models.user_roles import Role
from models.users import User
from security import get_password_hash
from config import DATABASE_URL
from config import ADMIN_USERNAME, ADMIN_EMAIL, ADMIN_PASSWORD
from config import FIXED_ROLES


ASYNC_DATABASE_URL = DATABASE_URL.replace(
    "postgresql://",
    "postgresql+asyncpg://",
    1,
)

engine = create_async_engine(
    ASYNC_DATABASE_URL,
    echo=False,
    pool_size=20, # Max number of connections in the pool
    max_overflow=2, # Max number of connections that can be created beyond the pool_size
)

AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

async def seed_roles_if_not_exist():
    """Seeds the database with fixed roles if they don't already exist. 
    This is useful for testing and initial setup.
    Args:
        None
    Returns:
        None
    """
    async with AsyncSessionLocal() as session:
        for role_name in FIXED_ROLES:
            result = await session.exec(select(Role).where(Role.name == role_name))
            exists = result.first()
            if not exists:
                session.add(Role(name=role_name))
        await session.commit()


async def create_admin_if_not_exists():
    """
    Creates an admin user if it doesn't exist. This is useful for testing and initial setup.
    In a production environment, you would want to handle user creation more securely.
    """
    async with AsyncSessionLocal() as session:
        result = await session.exec(select(User).where(User.is_admin == True))
        admin_user = result.first()
        if not admin_user:
            admin_user = User(
                username=ADMIN_USERNAME,
                email=ADMIN_EMAIL,
                hashed_password=get_password_hash(ADMIN_PASSWORD),
                is_admin=True,
                user_roles=[user_roles.Role(name="admin")]
            )
            session.add(admin_user)
            await session.commit()

async def create_db_and_tables():
    """
    Seeds startup data after Alembic has created and migrated the schema.
    """
    await seed_roles_if_not_exist()
    await create_admin_if_not_exists()



async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Creates a new session for each request and ensures it's closed after the request is done.
    This is a common pattern for database sessions in FastAPI.
    """
    async with AsyncSessionLocal() as session:
        """
        Use a context manager to ensure the session is properly closed after 
        the request is done, even if an error occurs.
        """
        yield session
