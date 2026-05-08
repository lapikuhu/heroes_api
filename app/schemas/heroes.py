"""Schemas are what is sent and received in the API requests and responses."""
from sqlmodel import SQLModel
from typing import Optional
from pydantic import Field

class HeroCreate(SQLModel):
    name: str = Field(index=True, title="Name of the hero", min_length=3)
    power: str = Field(index=True, title="Power of the hero", min_length=3)
    age: int | None = Field(default=None, index=True, title="Age of the hero")


class HeroUpdate(SQLModel):
    name: str | None = Field(default=None, index=True, title="Name of the hero")
    age: int | None = Field(default=None, index=True, title="Age of the hero")

### - Model Response Schemas - ###

class HeroRead(SQLModel):
    id: int
    name: str
    power: str
    age: int | None = None