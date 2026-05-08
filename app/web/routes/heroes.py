from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session

from dependencies import SessionDep
from services import heroes_service
from schemas.heroes import HeroCreate, HeroRead, HeroUpdate
router = APIRouter(prefix="/heroes", tags=["heroes"])

@router.get("/", tags=['heroes'], response_model=list[HeroRead], status_code=200)
def read_all_heroes(session: Session = Depends(SessionDep)):
    return heroes_service.get_all_heroes_service(session)

@router.get("/{hero_id}", tags=['heroes'], response_model=HeroRead, status_code=200)
def read_hero(hero_id: int, session: Session = Depends(SessionDep)):
    hero = heroes_service.get_hero_by_id(hero_id, session)
    if not hero:
        raise HTTPException(status_code=404, detail="Hero not found")
    return hero

@router.patch("/{hero_id}", tags=['heroes'], response_model=HeroRead, status_code=200)
def update_hero(hero_id: int, hero_update: HeroUpdate, session: Session = Depends(SessionDep)):
    hero = heroes_service.update_hero_by_id(hero_id, hero_update, session)
    if not hero:
        raise HTTPException(status_code=404, detail="Hero not found")
    return hero

@router.delete("/{hero_id}", tags=['heroes'], status_code=204)
def delete_hero(hero_id: int, session: Session = Depends(SessionDep)):
    success = heroes_service.delete_hero_by_id(hero_id, session)
    if not success:
        raise HTTPException(status_code=404, detail="Hero not found")
    return {"detail": "Hero deleted successfully"}