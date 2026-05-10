from sqlmodel import SQLModel, create_engine, Session, select
from models import user_roles
from dependencies import User
from security import get_password_hash
from config import DATABASE_URL, SECRET_KEY, ALGORITHM
from config import ADMIN_USERNAME, ADMIN_EMAIL, ADMIN_PASSWORD
from config import FIXED_ROLES
from sqlalchemy import create_engine as sa_create_engine, text


def create_database_if_not_exists():
    """Checks if the database exists, and creates it if it doesn't. 
    Args: 
        None
    Returns:
        None
    """
    default_url = DATABASE_URL.rsplit("/", 1)[0] + "/postgres"
    tmp_engine = sa_create_engine(default_url, isolation_level="AUTOCOMMIT")
    with tmp_engine.connect() as conn:
        exists = conn.execute(
            text("SELECT 1 FROM pg_database WHERE datname = 'heroes_db'")
        ).fetchone()
        if not exists:
            conn.execute(text("CREATE DATABASE heroes_db"))
    tmp_engine.dispose()


engine = create_engine(DATABASE_URL, 
                       echo=False,
                       pool_size=20, # Max number of connections in the pool
                       max_overflow=2) # Max number of connections that can be created beyond the pool_size

from models.user_roles import Role

def seed_roles_if_not_exist():
    """Seeds the database with fixed roles if they don't already exist. 
    This is useful for testing and initial setup.
    Args:
        None
    Returns:
        None
    """
    with Session(engine) as session:
        for role_name in FIXED_ROLES:
            exists = session.exec(select(Role).where(Role.name == role_name)).first()
            if not exists:
                session.add(Role(name=role_name))
        session.commit()

def create_admin_if_not_exists():
    """
    Creates an admin user if it doesn't exist. This is useful for testing and initial setup.
    In a production environment, you would want to handle user creation more securely.
    """
    with Session(engine) as session:
        admin_user = session.exec(select(User).where(User.is_admin == True)).first()
        if not admin_user:
            admin_user = User(
                username=ADMIN_USERNAME,
                email=ADMIN_EMAIL,
                hashed_password=get_password_hash(ADMIN_PASSWORD),
                is_admin=True,
                user_roles=[user_roles.Role(name="admin")]
            )
            session.add(admin_user)
            session.commit()

def create_db_and_tables():
    """
    Adds the tables and creates the database if they don't exist.
    In theory it can allow for revisions and migrations, but in practice
    it's better to use a tool like Alembic for that.
    """
    create_database_if_not_exists()
    create_admin_if_not_exists()
    SQLModel.metadata.create_all(engine)



def get_session():
    """
    Creates a new session for each request and ensures it's closed after the request is done.
    This is a common pattern for database sessions in FastAPI.
    """
    with Session(engine) as session:
        """
        Use a context manager to ensure the session is properly closed after 
        the request is done, even if an error occurs.
        """
        yield session