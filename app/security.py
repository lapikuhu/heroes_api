from sqlmodel import Session, select
from models import User
from services.users_service import get_user_by_username, create_user
from db import get_session
from typing import Annotated, Optional
from fastapi import Depends
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta, timezone
from config import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES
from fastapi import status, HTTPException

# Setup password hashing context using passlib
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
# OAuth2 scheme for token-based authentication
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token") # This tells FastAPI that the token will be obtained from the /token endpoint


def hash_password(raw: str) -> str:
    return pwd_context.hash(raw)
 
def verify_password(raw: str, hashed: str) -> bool:
    return pwd_context.verify(raw, hashed)
 
def create_access_token(sub: str) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    return jwt.encode({"sub": sub, "exp": expire}, SECRET_KEY, algorithm=ALGORITHM)

def get_current_user(
        token: Annotated[str, Depends(oauth2_scheme)],
        session: SessionDep
    ) -> User:
    """Get the current user based on the JWT token provided in the Authorization header.
    Args:
        token (str): The JWT token extracted from the Authorization header.
        session (Session): The database session for querying the user.
    Returns:
        User: The user object corresponding to the token's subject (username).
    Raises:
        HTTPException: If the token is invalid, expired, or if the user does not exist
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail = "Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"} # This header tells the client that it needs to provide a Bearer token for authentication
    )
    try:
        # Decode the JWT token to get the payload, which should contain the username in the "sub" field
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str | None = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    # Use SQLModel's select to query the database for a user with the given username
    user = session.exec(select(User).where(User.username == username)).first() # Query the database to get the user object based on the username
    if user is None:
        raise credentials_exception
    return user
