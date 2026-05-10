from fastapi import APIRouter, HTTPException, Depends

from dependencies import SessionDep, CurrentUser, AdminUser
from services import heroes_service
from schemas.heroes import HeroCreate, HeroRead, HeroUpdate
router = APIRouter(prefix="/heroes", tags=["heroes"])

@router.get("/", tags=['heroes'], 
            dependencies=None, # Public endpoint, no authentication required
            response_model=list[HeroRead], 
            status_code=200)
def read_all_heroes(session: SessionDep):
    return heroes_service.get_all_heroes_service(session)

@router.get("/{hero_id}", dependencies=None,
            tags=['heroes'], 
            response_model=HeroRead, 
            status_code=200)
def read_hero(hero_id: int, session: SessionDep):
    hero = heroes_service.get_hero_by_id(hero_id, session)
    if not hero:
        raise HTTPException(status_code=404, detail="Hero not found")
    return hero

@router.patch("/{hero_id}", tags=['heroes'], 
              dependencies=[Depends(CurrentUser)], # Authenticated users can update heroes, throws 401 if not authenticated
              response_model=HeroRead, 
              status_code=200)
def update_hero(hero_id: int, hero_update: HeroUpdate, session: SessionDep):
    hero = heroes_service.update_hero_by_id(hero_id, hero_update, session)
    if not hero:
        raise HTTPException(status_code=404, detail="Hero not found")
    return hero

@router.delete("/{hero_id}", tags=['heroes'], 
               dependencies=[Depends(AdminUser)], # Only admins can delete heroes, throws 403 if not authorized
               response_model=None, 
               status_code=204)
def delete_hero(hero_id: int, session: SessionDep):
    success = heroes_service.delete_hero_by_id(hero_id, session)
    if not success:
        raise HTTPException(status_code=404, detail="Hero not found")
    return {"detail": "Hero deleted successfully"}
