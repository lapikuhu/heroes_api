from db import AsyncSession as Session
from sqlmodel import select
from sqlalchemy.orm import selectinload
from models.heroes import Hero

async def create_hero(hero: Hero, session: Session) -> Hero:
    """ Write a hero to the database and return the created hero with its ID. 
    Args:
        hero (Hero): The hero data to be created.
        session (Session): The database session to use for the operation.
    Returns:
        Hero: The created hero with its ID.
    Raises:
        Exception: If there is an error during the database operation, it will 
        be rolled back and the exception will be propagated.
    """
    try:
        session.add(hero)
        await session.commit()
        await session.refresh(hero)
        return hero
    except Exception:
        await session.rollback()
        raise

async def is_existing_hero(name: str, session: Session) -> bool:
    """ Check if a hero with the given name already exists in the database.
    Args:
        name (str): The name of the hero to check for existence.
        session (Session): The database session to use for the operation.
    Returns:
        bool: True if a hero with the given name exists, False otherwise.
    """
    result = await session.exec(select(Hero).where(Hero.name == name))
    return result.first() is not None

async def get_hero(hero_id: int, session: Session) -> Hero | None:
    """Get a hero by ID. Returns None if the hero does not exist.
    Args:
        hero_id (int): The ID of the hero to retrieve.
        session (Session): The database session to use for the operation.
    Returns:
        Hero | None: The hero instance if found, otherwise None.
    """
    return await session.get(Hero, hero_id)

async def update_hero(hero_id: int, hero_data: Hero, session: Session) -> Hero | None:
    """Update a hero by ID. Returns the updated hero if successful, otherwise None.
    Args:
        hero_id (int): The ID of the hero to update.
        hero_data (Hero): The new data for the hero.
        session (Session): The database session to use for the operation.
    Returns:
        Hero | None: The updated hero instance if successful, otherwise None.
    """
    hero = await session.get(Hero, hero_id)
    if not hero:
        return None
    for key, value in hero_data.model_dump(exclude_unset=True).items():
        setattr(hero, key, value)
    try:
        session.add(hero)
        await session.commit()
        await session.refresh(hero)
        return hero
    except Exception:
        await session.rollback()
        raise

async def get_all_heroes(session: Session) -> list[Hero]:
    """Get a list of all heroes.
    Args:
        session (Session): The database session to use for the operation.
    Returns:
        list[Hero]: A list of all hero instances.
    """
    result = await session.exec(select(Hero))
    return result.all()

async def get_hero_mission_ids(hero_id: int, session: Session) -> list[int] | None:
    """Get the IDs of missions assigned to a hero by the hero's ID.
    Args:
        hero_id (int): The ID of the hero whose missions to retrieve.
        session (Session): The database session to use for the operation.
    Returns:
        list[int] | None: A list of mission IDs if the hero is found, otherwise None.
    """
    result = await session.exec(
        select(Hero)
        .where(Hero.id == hero_id)
        .options(selectinload(Hero.missions)) # Eagerly load missions to avoid lazy loading issues when accessing hero.missions
    )
    hero = result.one_or_none()

    if not hero:
        return None

    return [mission.id for mission in hero.missions]

async def delete_hero(hero_id: int, session: Session) -> bool:
    """Delete a hero by ID. Returns True if deletion was successful, False otherwise.
    Heroes with associated missions cannot be deleted.
    Args:
        hero_id (int): The ID of the hero to delete.
        session (Session): The database session to use for the operation.
    Returns:
        bool: True if deletion was successful, False otherwise.
    Raises:
        ValueError: If the hero is not found or if the hero has associated missions.
    """
    hero = await session.get(Hero, hero_id)
    if not hero:
        return False
    try:
        await session.delete(hero)
        await session.commit()
        return True
    except Exception:
        await session.rollback()
        raise