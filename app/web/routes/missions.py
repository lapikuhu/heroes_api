from fastapi import APIRouter, HTTPException, Depends

from dependencies import CurrentUser, SessionDep, AdminUser
from services import missions_service
from schemas.missions import MissionCreate, MissionReadById, MissionUpdate, MissionDelete

router = APIRouter(prefix="/missions", tags=["missions"])


@router.post("/", tags=['missions'], 
             dependencies=[Depends(CurrentUser)], # Authenticated users can create missions, throws 401 if not authenticated
             response_model=MissionReadById, 
             status_code=201)
def create_mission(mission_data: MissionCreate, session: SessionDep):
    return missions_service.create_mission(mission_data, session)

@router.get("/{mission_id}", 
            dependencies=None, # Public endpoint, no authentication required
            tags=['missions'], 
            response_model=MissionReadById, 
            status_code=200)
def read_mission(mission_id: int, session: SessionDep):
    mission = missions_service.get_mission_by_id(mission_id, session)
    if not mission:
        raise HTTPException(status_code=404, detail="Mission not found")
    return mission

@router.patch("/{mission_id}", tags=['missions'], 
              dependencies=[Depends(CurrentUser)], # Authenticated users can update missions, throws 401 if not authenticated
              response_model=MissionReadById, 
              status_code=200)
def update_mission(mission_id: int, mission_update: MissionUpdate, session: SessionDep):
    mission = missions_service.update_mission_by_id(mission_id, mission_update, session)
    if not mission:
        raise HTTPException(status_code=404, detail="Mission not found")
    return mission

@router.delete("/{mission_id}", tags=['missions'], 
               dependencies=[Depends(AdminUser)], # Only admins can delete missions, throws 403 if not authorized
               response_model=None, 
               status_code=204)
def delete_mission(mission_id: int, session: SessionDep):
    success = missions_service.delete_mission_by_id(mission_id, session)
    if not success:
        raise HTTPException(status_code=404, detail="Mission not found")
    return {"detail": "Mission deleted successfully"}