from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from app.persistence.configuration.database import get_db
from app.application.services.wine_services import WineServices
from app.application.dtos.wine.wine_for_view import WineRead
from app.application.dtos.wine.wine_for_create import WineCreate
from app.application.dtos.wine.wine_for_update import WineUpdate
from app.application.dtos.user.user_credentials import UserSession
from helpers.auth_user import current_user  

router = APIRouter(prefix="/wines", tags=["wines"])

def get_wine_service(db: AsyncSession = Depends(get_db)):
    return WineServices(db)

@router.get("/", response_model=List[WineRead])

async def list_wines(
      service: WineServices = Depends(get_wine_service),
      current_user: UserSession = Depends(current_user)
      ):
    return await service.list_wines(current_user)

@router.get("/{wine_id}", response_model=WineRead)
async def get_wine(wine_id: int, service: WineServices = Depends(get_wine_service)):
        wine = await service.get_by_id(wine_id)
        if not wine:
            raise HTTPException(status_code=404, detail="Wine not found")
        return wine

@router.post("/", response_model=WineRead, status_code=status.HTTP_201_CREATED)
async def create_wine(
      wine: WineCreate,
      service: WineServices = Depends(get_wine_service)):
    return await service.create(wine)

@router.patch("/{wine_id}", response_model=WineRead)
async def update_wine(wine_id: int, wine_update: WineUpdate, service: WineServices = Depends(get_wine_service)):
        updated = await service.update(wine_id, wine_update)
        if not updated:
            raise HTTPException(status_code=404, detail="Wine not found")
        return updated

@router.delete("/{wine_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_wine(wine_id: int, service: WineServices = Depends(get_wine_service)):
        deleted = await service.delete(wine_id)
        if not deleted:
            raise HTTPException(status_code=404, detail="Wine not found")