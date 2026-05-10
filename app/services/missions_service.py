### ----- MISSIONS SERVICE ----- ###
from sqlmodel import Session

from models.missions import Mission
from schemas.missions import MissionCreate, MissionUpdate
from repositories import missions_repo

def create_mission(mission_data: MissionCreate, session: Session) -> Mission:
    mission = Mission(
        name=mission_data.name,
        difficulty=mission_data.difficulty,
        completed=mission_data.completed,
        hero_id=mission_data.hero_id
    )
    mission = missions_repo.create_mission(mission, session=session)
    return mission

def get_mission_by_id(mission_id: int, session: Session) -> Mission | None:
    return missions_repo.get_mission(mission_id, session=session)

def update_mission_by_id(mission_id: int, mission_update_data: MissionUpdate, session: Session) -> Mission | None:
    mission_update = Mission(
        name=mission_update_data.name,
        difficulty=mission_update_data.difficulty,
        completed=mission_update_data.completed,
        hero_id=mission_update_data.hero_id
    )
    return missions_repo.update_mission(mission_id, mission_update, session=session)

def delete_mission_by_id(mission_id: int, session: Session) -> bool:
    return missions_repo.delete_mission(mission_id, session=session)

def get_missions_by_hero_id(hero_id: int, session: Session) -> list[Mission]:
    return missions_repo.get_missions_by_hero_id(hero_id, session=session)