### ----------------------------- USER ROUTERS ------------------------- ###
# Handle HTTP requests related to users. Routes call services to perform 
# business logic and return responses. Scehmas are used for request validation 
# and response models. Repositories are NEVER called directly by routes, only by 
# services.
# NOTE: User services are explicitly permission-awawre for deeper defense.
# Any changes in the routes have to be duplicated in # the service layer, so there are
# no mismatches between routes and services.

from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import OAuth2PasswordRequestForm
from typing import Annotated

# Local imports
from models import user_roles
from dependencies import CurrentUser, SessionDep, AdminUser, get_admin_user
from schemas.users import UserCreate, UserRead, UserCreatedResponse

from services import users_service

# Define the router for user-related endpoints
router = APIRouter(prefix="/users", tags=["users"])

###--------------------------- CREATE USER ------------------------- ###

@router.post("/register", 
             tags=["users"], 
             response_model=UserCreatedResponse, 
             dependencies=[Depends(get_admin_user)], # Only admins can create users, throws 403 if not admin
             status_code=201)
def create_user(user_data: UserCreate, session: SessionDep, admin_user: AdminUser):
    try:
        user = users_service.create_user_service(user_data, admin_user, session)
        return UserCreatedResponse(
            ok=True,
            user=UserRead(
                id=user.id,
                username=user.username,
                is_admin=user.is_admin,
                user_roles=[role.name for role in user.roles]
            ),
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    

###--------------------------- LOGIN ROUTE ------------------------- ###    

@router.post("/login", tags=["users"], status_code=200)
async def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()], session: SessionDep):
    """Authenticate user and return access token.
    Args:
        form_data (OAuth2PasswordRequestForm): The username and password provided in the login form.
        session (SessionDep): Database session dependency.
    Returns:
        dict: Access token and token type if authentication is successful.
    Raises:
        HTTPException: If authentication fails with status code 400 and error message.    
    """
    try:
        access_token, token_type = users_service.user_login_service(
            form_data.username, 
            form_data.password, 
            session=session)
        return {"access_token": access_token, "token_type": token_type}
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

###--------------------------- GET USER INFO ----------------------- ###

@router.get("/me", tags=["users"], 
            dependencies=[Depends(CurrentUser)], # authenticated users only, throws 401 if not authenticated 
            response_model=UserRead, status_code=200)
def get_me_user(current_user: CurrentUser):
    """Get the current authenticated user's information.
    Args:
        current_user (CurrentUser): The currently authenticated user, provided by dependency injection.
    Returns:
        UserRead: The current user's information, including id, username, admin status, and roles
    """
    return UserRead(
        id=current_user.id,
        username=current_user.username,
        is_admin=current_user.is_admin,
        user_roles=[role.name for role in current_user.roles]
    )

###------------------------ GET USER INFO BY USERNAME --------------------- ###

@router.get("/{username}", tags=["users"], response_model=UserRead, status_code=200)
def get_user_by_username(username: str, session: SessionDep):
    """Get user information by username.
    Args:
        username (str): The username of the user to retrieve.
        session (SessionDep): Database session dependency.
    Returns:
        UserRead: The user's information, including id, username, admin status, and roles.
    Raises:
        HTTPException: If the user is not found with status code 404.
    """
    user = users_service.get_user_by_username_service(username, session)

    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    
    return UserRead(
        id=user.id,
        username=user.username,
        is_admin=user.is_admin,
        user_roles=[role.name for role in user.roles]
    )

###---------------------------- UPDATE USER ------------------------ ###

@router.patch("/{user_id}", 
              tags=["users"], 
              response_model=UserRead, 
              dependencies=[Depends(get_admin_user)], # Only admins can update users, throws 403 if not admin
              status_code=200)
def update_user(user_id: int, user_data: UserCreate, session: SessionDep, admin_user: AdminUser):
    """Update user information. Only admins can update users.
    Args:
        user_id (int): The ID of the user to update.
        user_data (UserCreate): The new data for the user.
        session (SessionDep): Database session dependency.
        admin_user (AdminUser): The currently authenticated admin user, provided by dependency injection.
    Returns:
        UserRead: The updated user's information, including id, username, admin status, and roles
    Raises:
        HTTPException: If the user is not found with status code 404 or if validation fails with status code 400.  
    """
    try:
        user_update = users_service.update_user_service(user_id, user_data, admin_user, session)
        return UserRead(
            id=user_update.id,
            username=user_update.username,
            is_admin=user_update.is_admin,
            user_roles=[role.name for role in user_update.roles]
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

###--------------------------- DELETE USER ------------------------- ###

@router.delete("/{user_id}", 
               tags=["users"], 
               dependencies=[Depends(get_admin_user)], # Only admins can delete users, throws 403 if not admin
               status_code=204)
def delete_user(user_id: int, session: SessionDep, admin_user: AdminUser):
    """Delete a user. Only admins can delete users.
    Args:
        user_id (int): The ID of the user to delete.
        session (SessionDep): Database session dependency.
        admin_user (AdminUser): The currently authenticated admin user, provided by dependency injection.
    Raises:
        HTTPException: If the user is not found with status code 404.
    """
    users_service.delete_user_service(user_id, admin_user, session)