### -----------------------------   user schemas   ------------------------ ###
# Schemas are used for validation in services and for request/response models in routes. 
# They are not used for database models.
from sqlmodel import SQLModel, Field

class UserCreate(SQLModel):
    username: str = Field(index=True, title="Username of the user", min_length=3)
    password: str = Field(index=True, title="Password of the user", min_length=3)
    is_admin: bool = Field(default=False, index=True, title="Is admin")
    roles: list[str] = Field(default_factory=list, title="List of roles for the user")

class UserDelete(SQLModel):
    username: str = Field(index=True, title="Username of the user", min_length=3)

class UserUpdate(SQLModel):
    username: str | None = Field(default=None, index=True, title="Username of the user")
    password: str | None = Field(default=None, index=True, title="Password of the user")
    is_admin: bool | None = Field(default=None, index=True, title="Is admin")

class UserGetByUsername(SQLModel):
    username: str = Field(index=True, title="Username of the user", min_length=3)

class UserGetById(SQLModel):
    id: int = Field(index=True, title="ID of the user", gt=0)

class UserGetRolesById(SQLModel):
    id: int = Field(index=True, title="ID of the user", gt=0)

### ----------------------------- RESPONSE MODELS------------------------- ###
class UserRead(SQLModel):
    """Response model for reading user data"""
    id: int
    username: str
    is_admin: bool
    roles: list[str]

class UserCreatedResponse(SQLModel):
    """Response model for user creation"""
    ok: bool
    user: UserRead

class UserRolesResponse(SQLModel):
    """Response model for getting user roles"""
    roles: list[str]

class IsAdminResponse(SQLModel):
    """Response model for checking if user is admin"""
    is_admin: bool

class IsNotAdminResponse(SQLModel):
    """Response model for checking if user is not admin"""
    is_not_admin: bool