from fastapi import APIRouter, HTTPException, Depends

from dependencies import EditorUser, SessionDep, ViewerUser, get_admin_user
from services import heroes_service
from schemas.heroes import HeroCreate, HeroRead, HeroUpdate
router = APIRouter(prefix="/heroes", tags=["heroes"])



### ------------------------- CREATE HERO -------------------------- ###

@router.post("/", tags=['heroes'], 
             response_model=HeroRead, 
             status_code=201)
async def create_hero(hero: HeroCreate, session: SessionDep, editor_user: EditorUser):
    """Create a new hero. Requires editor or admin access.
    Args:
        hero (HeroCreate): The hero data to create.
        session (SessionDep): The database session dependency.
    Returns:
        HeroRead: The created hero data.    
    """
    return await heroes_service.create_hero(hero, session)

### --------------------- LIST OF ALL HEROES ----------------------- ###

@router.get("/", tags=['heroes'], 
            response_model=list[HeroRead], 
            status_code=200)
async def read_all_heroes(session: SessionDep, viewer_user: ViewerUser):
    """Get a list of all heroes. Requires viewer, editor, or admin access.
    Args:
        session (SessionDep): The database session dependency.
    Returns:
        list[HeroRead]: A list of all heroes.
    """
    return await heroes_service.get_all_heroes_service(session)

### ----------------------- GET HERO BY ID ------------------------- ###

@router.get("/{hero_id}",
            tags=['heroes'], 
            response_model=HeroRead, 
            status_code=200)
async def read_hero(hero_id: int, session: SessionDep, viewer_user: ViewerUser):
    """Get a hero by ID. Requires viewer, editor, or admin access.
    Args:
        hero_id (int): The ID of the hero to retrieve.
        session (SessionDep): The database session dependency.
    Returns:
        HeroRead: The hero data.
    Raises:
        HTTPException: If the hero is not found (404)."""
    hero = await heroes_service.get_hero_by_id(hero_id, session)
    if not hero:
        raise HTTPException(status_code=404, detail="Hero not found")
    return hero

### --------------------- UPDATE HERO BY ID ----------------------- ###

@router.patch("/{hero_id}", tags=['heroes'], 
              response_model=HeroRead, 
              status_code=200)
async def update_hero(hero_id: int, hero_update: HeroUpdate, session: SessionDep, editor_user: EditorUser):
    """Update a hero by ID. Requires editor or admin access.
    Args:
        hero_id (int): The ID of the hero to update.
        hero_update (HeroUpdate): The hero data to update.
        session (SessionDep): The database session dependency.
    Returns:
        HeroRead: The updated hero data.
    Raises:
        HTTPException: If the hero is not found (404)."""
    hero = await heroes_service.update_hero_by_id(hero_id, hero_update, session)
    if not hero:
        raise HTTPException(status_code=404, detail="Hero not found")
    return hero

### --------------------- DELETE HERO BY ID ----------------------- ###

@router.delete("/{hero_id}", tags=['heroes'], 
               dependencies=[Depends(get_admin_user)], # Only admins can delete heroes, throws 403 if not authorized
               response_model=None, 
               status_code=204)
async def delete_hero(hero_id: int, session: SessionDep):
    """Delete a hero by ID. Requires admin authentication.
    Args:
        hero_id (int): The ID of the hero to delete.
        session (SessionDep): The database session dependency.
    Raises:
        HTTPException: If the hero is not found (404) or cannot be deleted (400)."""
    user_success = await heroes_service.get_hero_by_id(hero_id, session)
    if not user_success:
        raise HTTPException(status_code=404, detail="Hero not found")
    success = await heroes_service.delete_hero_by_id(hero_id, session)
    if not success:
        raise HTTPException(status_code=400, detail="Cannot delete hero with assigned missions")
    return {"detail": "Hero deleted successfully"}
