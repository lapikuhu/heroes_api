from sqlalchemy.orm import foreign
from sqlmodel import SQLModel
from typing import Optional
from pydantic import Field

class MissionCreate(SQLModel):
    name: str = Field(index=True, title="Title of the mission", min_length=5)
    difficulty: int = Field(index=True, title="Difficulty level of the mission", ge=1, le=10)
    completed: bool = Field(index=True, title="Is the mission completed?", default=False)
    hero_id: int | None = Field(default=None, index=True, ge=1, title="ID of the hero assigned to the mission", foreign_key="hero.id")

class MissionReadById(SQLModel):
    name: str = Field(index=True, title="Title of the mission", min_length=5)
    difficulty: int = Field(index=True, title="Difficulty level of the mission", ge=1, le=10)
    completed: bool = Field(index=True, title="Is the mission completed?", default=False)
    hero_id: Optional[int] = Field(default=None, index=True, ge=1, title="ID of the hero assigned to the mission", foreign_key="hero.id")

class MissionUpdate(SQLModel):
    name: str | None = Field(default=None, index=True, title="Title of the mission")
    difficulty: int | None = Field(default=None, index=True, title="Difficulty level of the mission", ge=1, le=10)
    completed: bool | None = Field(default=None, index=True, title="Is the mission completed?")
    hero_id: int | None = Field(default=None, index=True, ge=1, title="ID of the hero assigned to the mission", foreign_key="hero.id")

class MissionGetHero(SQLModel):
    hero_id: int = Field(default=None, index=True, ge=1, title="ID of the hero assigned to the mission", foreign_key="hero.id")

class MissionDelete(SQLModel):
    id: int = Field(default=None, index=True, title="ID of the mission to delete")
