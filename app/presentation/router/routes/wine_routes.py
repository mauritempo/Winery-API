from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from fastapi.responses import JSONResponse

from app.application.dtos.stock_movement.stock_for_update import StockUpdate
from app.application.dtos.wine.wine_for_update_stock import WineStockUpdate
from app.application.dtos.wine.wine_paginated import PaginatedWines
from app.persistence.configuration.database import get_db
from app.application.services.wine_services import WineServices
from app.application.dtos.wine.wine_for_view import WineRead
from app.application.dtos.wine.wine_for_create import WineCreate
from app.application.dtos.wine.wine_for_update import WineUpdate
from app.application.dtos.user.user_credentials import UserSession
from helpers.auth_user import current_user  

class WineRouter:
    router = APIRouter(prefix="/wines", tags=["wines"])

    def get_wine_service(db: AsyncSession = Depends(get_db)):
        return WineServices(db, db)
    
    @router.get("/paginated-wines", response_model=PaginatedWines)
    async def list_paginated_wines(
        offset: int = Query(0, ge=0),
        limit: int = Query(10, gt=0, le=100),
        service: WineServices = Depends(get_wine_service),
        current_user: UserSession = Depends(current_user)
    ):
        return await service.list_paginated_wines(current_user, offset=offset, limit=limit)


    @router.get("/", response_model=List[WineRead])
    async def list_wines(
        service: WineServices = Depends(get_wine_service),
        current_user: UserSession = Depends(current_user)
        ):
        return await service.list_wines(current_user)
    
    @router.get("/public", response_model=list[WineRead], status_code=status.HTTP_200_OK)
    async def list_public_wines(service: WineServices = Depends(get_wine_service)):
        return await service.list_public_wines()


    @router.get("/{wine_id}", response_model=WineRead)
    async def get_wine(wine_id: int, service: WineServices = Depends(get_wine_service),current_user: UserSession = Depends(current_user) ):
            wine = await service.get_by_id(wine_id, current_user)
            if not wine:
                raise HTTPException(status_code=404, detail="Wine not found")
            return wine
    

    @router.post("/", response_model=WineRead, status_code=status.HTTP_201_CREATED)
    async def create_wine(wine: WineCreate,service: WineServices = Depends(get_wine_service)):
        return await service.create(wine)

    @router.patch("/{wine_id}", response_model=WineRead)
    async def update_wine(wine_id: int, wine_update: WineUpdate, service: WineServices = Depends(get_wine_service), current_user: UserSession = Depends(current_user)):
        return await service.update(wine_id, wine_update,current_user)

    @router.delete("/{wine_id}", status_code=status.HTTP_200_OK)
    async def delete_wine(wine_id: int, service: WineServices = Depends(get_wine_service), current_user: UserSession = Depends(current_user)) -> JSONResponse:
        return await service.delete(wine_id, current_user)
    
    @router.put("/{wine_id}/stock", response_model=WineStockUpdate, status_code=status.HTTP_200_OK)
    async def set_stock(
        wine_id: int,
        stock_update: StockUpdate,
        service: WineServices = Depends(get_wine_service),
        current_user: UserSession = Depends(current_user)
    ):
        return await service.set_stock(wine_id, stock_update,current_user)

