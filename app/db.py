from sqlmodel import SQLModel, create_engine, Session

DATABASE_URL = ""
engine = create_engine(DATABASE_URL, 
                       echo=False,
                       connect_args={"check_same_thread": False}, # Required for SQLite to allow multiple threads to access the database
                       pool_size=20, # Max number of connections in the pool
                       max_overflow=2) # Max number of connections that can be created beyond the pool_size

def create_db_and_tables():
    """
    Adds the tables and creates the database if they don't exist.
    In theory it can allow for revisions and migrations, but in practice
    it's better to use a tool like Alembic for that.
    """
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