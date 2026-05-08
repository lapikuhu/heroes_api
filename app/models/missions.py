from sqlmodel import Field, Relationship, SQLModel

class Mission(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(index=True, title="Title of the mission", min_length=5)
    difficulty: int = Field(index=True, title="Difficulty level of the mission", ge=1, le=10)
    completed: bool = Field(index=True, title="Is the mission completed?", default=False)
    hero_id: int | None = Field(default=None, foreign_key="hero.id")
    
    