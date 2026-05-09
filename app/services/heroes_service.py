### ----- HEROES SERVICE ----- ###
# Business logic for handling heroes-related operations.
# Invoke repository functions to interact with the database and perform 
# necessary checks or transformations.
from models.heroes import Hero
from schemas.heroes import HeroCreate, HeroUpdate
from sqlmodel import Session
from repositories import heroes_repo


def create_hero(hero_data: HeroCreate, session: Session) -> Hero:
    if heroes_repo.is_existing_hero(hero_data.name, session):
        raise ValueError("Hero with this name already exists")
    hero = Hero(
        name=hero_data.name,
        power=hero_data.power,
        age=hero_data.age,
    )
    return heroes_repo.create_hero(hero, session)

def get_hero_by_id(hero_id: int, session: Session) -> Hero | None:
    return heroes_repo.get_hero(hero_id, session)

def update_hero_by_id(hero_id: int, hero_data: HeroUpdate, session: Session) -> Hero | None:
    return heroes_repo.update_hero(hero_id, hero_data, session)

def get_all_heroes_service(session: Session) -> list[Hero]:
    return heroes_repo.get_all_heroes(session)

def delete_hero_by_id(hero_id: int, session: Session) -> bool:
    return heroes_repo.delete_hero(hero_id, session)
