from fastapi import HTTPException, status
from jose import JWTError
from sqlmodel import Session

from models.users import User
from repositories import users_repo
from security import decode_access_token


def get_current_user(token: str, session: Session) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = decode_access_token(token)
        username: str | None = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = users_repo.get_user_by_username(username, session)
    if user is None:
        raise credentials_exception
    return user
