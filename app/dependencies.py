from sqlmodel import Session
from models import User
from services.users_service import get_current_user
from db import get_session
from typing import Annotated, Optional
from fastapi import Depends

# Dependency for getting a database session
SessionDep = Annotated[Session, Depends(get_session)]

# Create the current user dependency for FastAPI routes
CurrentUser = Annotated[User, Depends(get_current_user)]