from sqlmodel import Session
from models.heroes import Hero

def create_hero(hero: Hero, session: Session) -> Hero:
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
        session.commit()
        session.refresh(hero)
        return hero
    except Exception:
        session.rollback()
        raise

def is_existing_hero(name: str, session: Session) -> bool:
    """ Check if a hero with the given name already exists in the database.
    Args:
        name (str): The name of the hero to check for existence.
        session (Session): The database session to use for the operation.
    Returns:
        bool: True if a hero with the given name exists, False otherwise.
    """
    return session.exec(Hero).filter(Hero.name == name).first() is not None

def get_hero(hero_id: int, session: Session) -> Hero | None:
    return session.get(Hero, hero_id)

def update_hero(hero_id: int, hero_data: Hero, session: Session) -> Hero | None:
    hero = session.get(Hero, hero_id)
    if not hero:
        return None
    for key, value in hero_data.dict(exclude_unset=True).items():
        setattr(hero, key, value)
    try:
        session.add(hero)
        session.commit()
        session.refresh(hero)
        return hero
    except Exception:
        session.rollback()
        raise

def get_all_heroes(session: Session) -> list[Hero]:
    return session.exec(Hero).all()

def get_hero_mission_ids(hero_id: int, session: Session) -> list[int] | None:
    hero = session.get(Hero, hero_id)
    if not hero:
        return None
    return [mission.id for mission in hero.missions]

def delete_hero(hero_id: int, session: Session) -> bool:
    hero = session.get(Hero, hero_id)
    if not hero:
        return False
    try:
        session.delete(hero)
        session.commit()
        return True
    except Exception:
        session.rollback()
        raise