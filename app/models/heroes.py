from sqlmodel import Field, Relationship, SQLModel, default
from typing import TYPE_CHECKING

if TYPE_CHECKING: # Avoid circular imports by only importing Mission for type checking
    from models.missions import Mission

class Hero(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(index=True, title="Name of the hero", min_length=3)
    power: str = Field(index=True, title="Power of the hero", min_length=3)
    age: int | None = Field(default=None, index=True, title="Age of the hero")
    missions: list["Mission"] = Relationship(back_populates="hero")
