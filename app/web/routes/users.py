### ----------------------------- USER ROUTERS ------------------------- ###
# Handle HTTP requests related to users. Routes call services to perform 
# business logic and return responses. Scehmas are used for request validation 
# and response models. Repositories are NEVER called directly by routes, only by 
# services.
from fastapi import APIRouter, HTTPException

from dependencies import SessionDep
from schemas.users import UserCreate, UserRead, UserCreatedResponse
from services import users_service

# Define the router for user-related endpoints
router = APIRouter(prefix="/users", tags=["users"])

@router.post("/", tags=["users"], response_model=UserCreatedResponse, status_code=201)
def create_user(user_data: UserCreate, session: SessionDep):
    try:
        user = users_service.create_user_service(user_data, session)
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


@router.get("/{username}", tags=["users"], response_model=UserRead, status_code=200)
def get_user_by_username(username: str, session: SessionDep):
    user = users_service.get_user_by_username_service(username, session)

    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    
    return UserRead(
        id=user.id,
        username=user.username,
        is_admin=user.is_admin,
    )

@router.patch("/{user_id}", tags=["users"], response_model=UserRead, status_code=200)
def update_user(user_id: int, user_data: UserCreate, session: SessionDep):
    try:
        user = users_service.update_user_service(user_id, user_data, session)
        return UserRead(
            id=user.id,
            username=user.username,
            is_admin=user.is_admin,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

@router.delete("/{user_id}", tags=["users"], status_code=204)
def delete_user(user_id: int, session: SessionDep):
    users_service.delete_user_service(user_id, session)