### ----- HEROES SERVICE ----- ###
# Business logic for handling heroes-related operations.
# Invoke repository functions to interact with the database and perform 
# necessary checks or transformations.
# Shallow defence: access control is handled at the route level.

from models.users import User
from models.heroes import Hero
from schemas.heroes import HeroCreate, HeroUpdate
from sqlmodel import Session
from repositories import heroes_repo

### ------------------------- CREATE HERO -------------------------- ###

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

def get_hero_mission_ids_service(hero_id: int, session: Session) -> list[int] | None:
    """Service function to get the list of mission IDs assigned to a hero by their ID.
    Args:
        hero_id (int): The ID of the hero for whom to retrieve mission IDs.
        session (Session): The database session to use for the operation.
    Returns:
        list[int] | None: A list of mission IDs assigned to the hero, or None if the hero does not exist.
    """
    return heroes_repo.get_hero_mission_ids(hero_id, session)

def delete_hero_by_id(hero_id: int, session: Session) -> bool:
    """Delete a hero by ID. Returns True if deletion was successful, False otherwise.
    Heroes with associated missions cannot be deleted.
    """
    if get_hero_by_id(hero_id, session) is None:
        raise ValueError("Hero not found")
    if len(get_hero_mission_ids_service(hero_id, session) or []) > 0:
        raise ValueError("Cannot delete hero with assigned missions")
    return heroes_repo.delete_hero(hero_id, session)
