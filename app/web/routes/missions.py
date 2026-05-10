from webbrowser import get

from fastapi import APIRouter, HTTPException, Depends

# Local imports
from dependencies import CurrentUser, SessionDep, AdminUser, get_current_user, get_admin_user
from services import missions_service
from services.heroes_service import get_hero_by_id
from schemas.missions import MissionCreate, MissionReadById, MissionUpdate, MissionDelete

router = APIRouter(prefix="/missions", tags=["missions"])

### ------------------------ CREATE MISSION ------------------------ ###

@router.post("/", tags=['missions'], 
             dependencies=[Depends(get_current_user)], # Authenticated users can create missions, throws 401 if not authenticated
             response_model=MissionReadById, 
             status_code=201)
async def create_mission(mission_data: MissionCreate, session: SessionDep):
    """Create a new mission. Requires authentication.
    Args:
        mission_data (MissionCreate): The data for the mission to be created.
        session (SessionDep): The database session to use for the operation.
    Returns:
        MissionReadById: The created mission.
    Raises:
        HTTPException: If the hero specified in the mission data does not exist (404).
        HTTPException: If the user is not authenticated (401) or if there is an error during mission creation (400).
    """
    if mission_data.hero_id is not None and not await get_hero_by_id(mission_data.hero_id, session):
        raise HTTPException(status_code=404, detail="Hero not found")
    return await missions_service.create_mission(mission_data, session)

### ----------------------- READ ALL MISSIONS ---------------------- ###

@router.get("/", tags=['missions'], 
            dependencies=None, # Public endpoint, no authentication required
            response_model=list[MissionReadById], 
            status_code=200)
async def read_all_missions(session: SessionDep):
    """Retrieve all missions. Public endpoint, no authentication required.
    Args:
        session (SessionDep): The database session to use for the operation.
    Returns:
        list[MissionReadById]: A list of all missions.
    Raises:        HTTPException: If there is an error during retrieval of missions (400).
    """
    return await missions_service.get_all_missions(session)

### ------------------------- READ MISSION ------------------------- ###

@router.get("/{mission_id}", 
            dependencies=None, # Public endpoint, no authentication required
            tags=['missions'], 
            response_model=MissionReadById, 
            status_code=200)
async def read_mission(mission_id: int, session: SessionDep):
    mission = await missions_service.get_mission_by_id(mission_id, session)
    if not mission:
        raise HTTPException(status_code=404, detail="Mission not found")
    return mission

### ----------------------- UPDATE MISSION ----------------------- ###

@router.patch("/{mission_id}", tags=['missions'], 
              dependencies=[Depends(get_current_user)], # Authenticated users can update missions, throws 401 if not authenticated
              response_model=MissionReadById, 
              status_code=200)
async def update_mission(mission_id: int, mission_update: MissionUpdate, session: SessionDep):
    mission = await missions_service.update_mission_by_id(mission_id, mission_update, session)
    if not mission:
        raise HTTPException(status_code=404, detail="Mission not found")
    return mission


### ------------------------ DELETE MISSION ------------------------ ###

@router.delete("/{mission_id}", tags=['missions'], 
               dependencies=[Depends(get_admin_user)], # Only admins can delete missions, throws 403 if not authorized
               response_model=None, 
               status_code=204)
async def delete_mission(mission_id: int, session: SessionDep):
    success = await missions_service.delete_mission_by_id(mission_id, session)
    if not success:
        raise HTTPException(status_code=404, detail="Mission not found")
    return {"detail": "Mission deleted successfully"}