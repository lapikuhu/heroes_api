### ----------------------------- USER ROUTERS ------------------------- ###
# Handle HTTP requests related to users. Routes call services to perform 
# business logic and return responses. Scehmas are used for request validation 
# and response models. Repositories are NEVER called directly by routes, only by 
# services.
from os import access

from fastapi import APIRouter, HTTPException, Depends

from models import user_roles
from dependencies import CurrentUser, SessionDep, AdminUser, get_admin_user
from schemas.users import UserCreate, UserRead, UserCreatedResponse, UserCreds
from services import users_service

# Define the router for user-related endpoints
router = APIRouter(prefix="/users", tags=["users"])

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
            ),
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    

###--------------------------- LOGIN ROUTE ------------------------- ###    

@router.post("/login", tags=["users"], status_code=200)
def login_user(session: SessionDep, user_creds: UserCreds):
    """Authenticate user and return access token.
    Args:
        session (SessionDep): Database session dependency.
        user_creds (UserCreds): User credentials for login.
    Returns:
        dict: Access token and token type if authentication is successful.
    Raises:
        HTTPException: If authentication fails with status code 400 and error message.    
    """
    try:
        access_token, token_type = users_service.user_login_service(user_creds.username, user_creds.password, session)
        return {"access_token": access_token, "token_type": token_type}
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

###--------------------------- GET USER INFO ----------------------- ###

@router.get("/me", tags=["users"], response_model=UserRead, status_code=200)
def get_me_user(current_user: CurrentUser):
    """Get the current authenticated user's information."""
    return UserRead(
        id=current_user.id,
        username=current_user.username,
        is_admin=current_user.is_admin,
        user_roles=[role.name for role in current_user.roles]
    )

@router.get("/{username}", tags=["users"], response_model=UserRead, status_code=200)
def get_user_by_username(username: str, session: SessionDep):
    user = users_service.get_user_by_username_service(username, session)

    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    
    return UserRead(
        id=user.id,
        username=user.username,
        is_admin=user.is_admin,
        user_roles=[role.name for role in user.roles]
    )

@router.patch("/{user_id}", 
              tags=["users"], 
              response_model=UserRead, 
              dependencies=[Depends(get_admin_user)], # Only admins can update users, throws 403 if not admin
              status_code=200)

def update_user(user_id: int, user_data: UserCreate, session: SessionDep, admin_user: AdminUser):
    try:
        user = users_service.update_user_service(user_id, user_data, admin_user, session)
        return UserRead(
            id=user.id,
            username=user.username,
            is_admin=user.is_admin,
            user_roles=[role.name for role in user.roles]
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

@router.delete("/{user_id}", 
               tags=["users"], 
               dependencies=[Depends(get_admin_user)], # Only admins can delete users, throws 403 if not admin
               status_code=204)
def delete_user(user_id: int, session: SessionDep, admin_user: AdminUser):
    users_service.delete_user_service(user_id, admin_user, session)