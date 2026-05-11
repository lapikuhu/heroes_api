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
    return await session.get(Hero, hero_id)

async def update_hero(hero_id: int, hero_data: Hero, session: Session) -> Hero | None:
    hero = await session.get(Hero, hero_id)
    if not hero:
        return None
    for key, value in hero_data.dict(exclude_unset=True).items():
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
    result = await session.exec(select(Hero))
    return result.all()

async def get_hero_mission_ids(hero_id: int, session: Session) -> list[int] | None:
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