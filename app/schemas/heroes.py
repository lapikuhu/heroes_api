"""Schemas are what is sent and received in the API requests and responses."""
from sqlmodel import SQLModel
from pydantic import Field

class HeroCreate(SQLModel):
    name: str = Field(title="Name of the hero", min_length=3)
    power: str = Field(title="Power of the hero", min_length=3)
    age: int | None = Field(default=None, title="Age of the hero")


class HeroUpdate(SQLModel):
    name: str | None = Field(default=None, title="Name of the hero")
    age: int | None = Field(default=None, title="Age of the hero")

### - Model Response Schemas - ###

class HeroRead(SQLModel):
    id: int
    name: str
    power: str
    age: int | None = None
    mission_ids: list[int] = Field(default_factory=list, title="List of mission IDs assigned to the hero")

class HeroMissionIDsResponse(SQLModel):
    mission_ids: list[int] = Field(default_factory=list, title="List of mission IDs assigned to the hero")