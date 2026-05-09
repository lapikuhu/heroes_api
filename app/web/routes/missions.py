from re import A

from fastapi import APIRouter, HTTPException

from dependencies import SessionDep
from services import missions_service
from schemas.missions import MissionCreate, MissionReadById, MissionUpdate, MissionDelete

router = APIRouter(prefix="/missions", tags=["missions"])


@router.post("/", tags=['missions'], response_model=MissionReadById, status_code=201)
def create_mission(mission_data: MissionCreate, session: SessionDep):
    return missions_service.create_mission(mission_data, session)

@router.get("/{mission_id}", tags=['missions'], response_model=MissionReadById, status_code=200)
def read_mission(mission_id: int, session: SessionDep):
    mission = missions_service.get_mission_by_id(mission_id, session)
    if not mission:
        raise HTTPException(status_code=404, detail="Mission not found")
    return mission

@router.patch("/{mission_id}", tags=['missions'], response_model=MissionReadById, status_code=200)
def update_mission(mission_id: int, mission_update: MissionUpdate, session: SessionDep):
    mission = missions_service.update_mission_by_id(mission_id, mission_update, session)
    if not mission:
        raise HTTPException(status_code=404, detail="Mission not found")
    return mission

@router.delete("/{mission_id}", tags=['missions'], response_model=None, status_code=204)
def delete_mission(mission_id: int, session: SessionDep):
    success = missions_service.delete_mission_by_id(mission_id, session)
    if not success:
        raise HTTPException(status_code=404, detail="Mission not found")
    return {"detail": "Mission deleted successfully"}