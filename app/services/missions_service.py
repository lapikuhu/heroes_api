### ----- MISSIONS SERVICE ----- ###
from db import AsyncSession as Session

from models.missions import Mission
from schemas.missions import MissionCreate, MissionUpdate
from repositories import missions_repo

async def create_mission(mission_data: MissionCreate, session: Session) -> Mission:
    """Create a new mission.
    Args:
        mission_data (MissionCreate): The data for the mission to be created.
        session (Session): The database session to use for the operation.
    Returns:
        Mission: The created mission instance.
    Raises:
        ValueError: If there is an error during mission creation (e.g., invalid data)."""
    mission = Mission(
        name=mission_data.name,
        difficulty=mission_data.difficulty,
        completed=mission_data.completed,
        hero_id=mission_data.hero_id
    )
    mission = await missions_repo.create_mission(mission, session=session)
    return mission

async def get_all_missions(session: Session) -> list[Mission]:
    """Get a list of all missions.
    Args:
        session (Session): The database session to use for the operation.
    Returns:
        list[Mission]: A list of all mission instances.
    """
    return await missions_repo.get_all_missions(session=session)

async def get_mission_by_id(mission_id: int, session: Session) -> Mission | None:
    """Get a mission by ID. Returns None if the mission does not exist.
    Args:
        mission_id (int): The ID of the mission to retrieve.
        session (Session): The database session to use for the operation.
    Returns:
        Mission | None: The mission instance if found, otherwise None.
    """
    return await missions_repo.get_mission(mission_id, session=session)

async def update_mission_by_id(mission_id: int, mission_update_data: MissionUpdate, session: Session) -> Mission | None:
    """Update a mission by ID. Returns the updated mission or None if the mission does not exist.
    Args:        mission_id (int): The ID of the mission to update.
        mission_update_data (MissionUpdate): The data to update the mission with.
        session (Session): The database session to use for the operation.
    Returns:
        Mission | None: The updated mission instance if found, otherwise None.
    """
    return await missions_repo.update_mission(mission_id, mission_update_data, session=session)

async def delete_mission_by_id(mission_id: int, session: Session) -> bool:
    """Delete a mission by ID. Returns True if deletion was successful, False otherwise.
    Args:
        mission_id (int): The ID of the mission to delete.
        session (Session): The database session to use for the operation.
    Returns:
        bool: True if deletion was successful, False otherwise.
    """
    return await missions_repo.delete_mission(mission_id, session=session)

async def get_missions_by_hero_id(hero_id: int, session: Session) -> list[Mission]:
    """Get a list of missions assigned to a hero by the hero's ID.
    Args:
        hero_id (int): The ID of the hero for whom to retrieve missions.
        session (Session): The database session to use for the operation.
    Returns:
        list[Mission]: A list of missions assigned to the hero.
    """
    return await missions_repo.look_up_mission_by_hero_id(hero_id, session=session)
