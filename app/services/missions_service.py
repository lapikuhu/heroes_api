### ----- MISSIONS SERVICE ----- ###
from db import AsyncSession as Session

from models.missions import Mission
from schemas.missions import MissionCreate, MissionUpdate
from repositories import missions_repo

async def create_mission(mission_data: MissionCreate, session: Session) -> Mission:
    mission = Mission(
        name=mission_data.name,
        difficulty=mission_data.difficulty,
        completed=mission_data.completed,
        hero_id=mission_data.hero_id
    )
    mission = await missions_repo.create_mission(mission, session=session)
    return mission

async def get_all_missions(session: Session) -> list[Mission]:
    return await missions_repo.get_all_missions(session=session)

async def get_mission_by_id(mission_id: int, session: Session) -> Mission | None:
    return await missions_repo.get_mission(mission_id, session=session)

async def update_mission_by_id(mission_id: int, mission_update_data: MissionUpdate, session: Session) -> Mission | None:
    mission_update = Mission(
        name=mission_update_data.name,
        difficulty=mission_update_data.difficulty,
        completed=mission_update_data.completed,
        hero_id=mission_update_data.hero_id
    )
    return await missions_repo.update_mission(mission_id, mission_update, session=session)

async def delete_mission_by_id(mission_id: int, session: Session) -> bool:
    return await missions_repo.delete_mission(mission_id, session=session)

async def get_missions_by_hero_id(hero_id: int, session: Session) -> list[Mission]:
    return await missions_repo.look_up_mission_by_hero_id(hero_id, session=session)