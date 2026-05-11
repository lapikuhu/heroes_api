from sqlalchemy.orm import foreign
from sqlmodel import SQLModel
from typing import Optional
from pydantic import Field

class MissionCreate(SQLModel):
    name: str = Field(title="Title of the mission", min_length=5)
    difficulty: int = Field(title="Difficulty level of the mission", ge=1, le=10)
    completed: bool = Field(title="Is the mission completed?", default=False)
    hero_id: int | None = Field(default=None, ge=1, title="ID of the hero assigned to the mission")

class MissionReadById(SQLModel):
    id: int = Field(title="ID of the mission")
    name: str = Field(title="Title of the mission", min_length=5)
    difficulty: int = Field(title="Difficulty level of the mission", ge=1, le=10)
    completed: bool = Field(title="Is the mission completed?", default=False)
    hero_id: Optional[int] = Field(default=None, ge=1, title="ID of the hero assigned to the mission")

class MissionUpdate(SQLModel):
    name: str | None = Field(default=None, title="Title of the mission")
    difficulty: int | None = Field(default=None, title="Difficulty level of the mission", ge=1, le=10)
    completed: bool | None = Field(default=None, title="Is the mission completed?")
    hero_id: int | None = Field(default=None, ge=1, title="ID of the hero assigned to the mission")

class MissionGetHero(SQLModel):
    hero_id: int = Field(default=None, ge=1, title="ID of the hero assigned to the mission")

class MissionDelete(SQLModel):
    id: int = Field(default=None, title="ID of the mission to delete")
