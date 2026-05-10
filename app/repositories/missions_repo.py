from sqlmodel import select
from db import AsyncSession as Session
from models.missions import Mission
from schemas.missions import MissionCreate, MissionUpdate

async def create_mission(mission: Mission, session: Session) -> Mission:
    """ Write a mission to the database and return the created mission with its ID. 
    Args:
        mission (Mission): The mission data to be created.
        session (Session): The database session to use for the operation.
    Returns:
        Mission: The created mission with its ID.
    Raises:
        Exception: If there is an error during the database operation, it will 
        be rolled back and the exception will be propagated.
    """
    try:
        session.add(mission)
        await session.commit()
        await session.refresh(mission)
        return mission
    except Exception:
        await session.rollback()
        raise

async def get_mission(mission_id: int, session: Session) -> Mission | None:
    """ Retrieve a mission from the database by its ID. 
    Args:
        mission_id (int): The ID of the mission to retrieve.
        session (Session): The database session to use for the operation.
    Returns:
        Mission | None: The retrieved mission if found, otherwise None.
    """
    return await session.get(Mission, mission_id)

async def get_all_missions(session: Session) -> list[Mission]:
    """ Retrieve all missions from the database. 
    Args:
        session (Session): The database session to use for the operation.

    Returns:
        list[Mission]: A list of all missions in the database.
    """
    return (await session.exec(select(Mission))).all()

async def update_mission(mission_id: int, mission_data: MissionUpdate, session: Session) -> Mission | None:
    """ Update an existing mission in the database. 
    Args:
        mission_id (int): The ID of the mission to update.
        mission_data (Mission): The new data for the mission.
        session (Session): The database session to use for the operation.
    Returns:
        Mission | None: The updated mission if found and updated, otherwise None.
    Raises:
        Exception: If there is an error during the database operation, it will 
        be rolled back and the exception will be propagated.
    """
    try:
        mission = await session.get(Mission, mission_id)
        if not mission:
            return None
        for key, value in mission_data.model_dump(exclude_unset=True).items():
            setattr(mission, key, value)
        await session.commit()
        await session.refresh(mission)
        return mission
    except Exception:
        await session.rollback()
        raise

async def delete_mission(mission_id: int, session: Session) -> bool:
    """ Delete a mission from the database by its ID. 
    Args:
        mission_id (int): The ID of the mission to delete.
        session (Session): The database session to use for the operation.
    Returns:
        bool: True if the mission was found and deleted, False otherwise.
    Raises:
        Exception: If there is an error during the database operation, it will 
        be rolled back and the exception will be propagated.
    """
    try:
        mission = await session.get(Mission, mission_id)
        if not mission:
            return False
        await session.delete(mission)
        await session.commit()
        return True
    except Exception:
        await session.rollback()
        raise

async def look_up_mission_by_hero_id(hero_id: int, session: Session) -> list[Mission]:
    """ Look up missions assigned to a specific hero by the hero's ID. 
    Args:
        hero_id (int): The ID of the hero whose missions to look up.
        session (Session): The database session to use for the operation.
    Returns:
        list[Mission]: A list of missions assigned to the specified hero.
    """
    return (await session.exec(select(Mission).where(Mission.hero_id == hero_id))).all()