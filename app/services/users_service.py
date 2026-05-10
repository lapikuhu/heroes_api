### ----------------------------- USER SERVICES------------------------- ###
# Business logic for user operations. Services are called by routes and 
# call repositories to interact with the database.
from models.users import User
from models.user_roles import Role
from repositories import users_repo
from schemas.users import UserCreate, UserIsAdminResponse
from security import hash_password, verify_password, create_access_token
from sqlmodel import Session


def create_user_service(user_data: UserCreate, editor_is_admin: UserIsAdminResponse, session: Session) -> User:
    """Create a new user. Only admins can create other users.
    Args:
        user_data (UserCreate): Data for the new user.
        editor_is_admin (UserIsAdminResponse): Whether the user creating the new user is an admin.
        session (Session): Database session.
    Returns:
        User: The created user.
    Raises:
        ValueError: If the username already exists or if a non-admin tries to create an admin
  """
    if users_repo.is_existing_user(user_data.username, session):
        raise ValueError("Username already exists")
    
    if editor_is_admin.is_admin is False:
        raise ValueError("Only admins can create other admin users")
    else:
        user = User(
            username=user_data.username,
            hashed_password=hash_password(user_data.password),
            is_admin=editor_is_admin.is_admin,
            roles=[Role(name=role_name) for role_name in user_data.roles]
        )
    return users_repo.create_user(user, session)

def get_user_by_username_service(username: str, session: Session) -> User | None:
    return users_repo.get_user_by_username(username, session)

def get_user_by_id_service(user_id: int, session: Session) -> User | None:
    return users_repo.get_user_by_id(user_id, session)

def get_user_roles_by_id_service(user_id: int, session: Session) -> list[str] | None:
    return users_repo.get_user_roles_by_id(user_id, session)

def user_login_service(username: str, password: str, session: Session) -> tuple[str, str] | None:
    """Authenticate user and return access token if valid.
    Args:
        username (str): Username of the user trying to log in.
        password (str): Password of the user trying to log in.
        session (Session): Database session.
    Returns:
        tuple[str, str]: Access token and token type if authentication is successful.
    Raises:
        ValueError: If authentication fails due to invalid username or password.
    """
    user = users_repo.get_user_by_username(username, session)
    if user and verify_password(password, user.hashed_password):
        # Generate token (this is a placeholder, implement actual token generation)
        access_token = create_access_token(username)
        token_type = "bearer"
        return access_token, token_type
    else:
        raise ValueError("Invalid username or password")          

