from sqlalchemy.exc import IntegrityError
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException
from fastapi.responses import JSONResponse

from app.application.dtos.stock_movement.stock_for_read import StockMovementRead
from app.application.dtos.stock_movement.stock_for_update import StockUpdate
from app.application.dtos.user.user_credentials import UserSession
from app.application.dtos.wine.wine_for_update_stock import WineStockUpdate
from app.application.dtos.wine.wine_paginated import PaginatedWines
from app.domain.entities.wine import Wine
from app.persistence.repository.wine_repository import WineRepository
from app.persistence.repository.stock_movement_repository import StockMovementRepository
from app.application.services.location_services import LocationServices
from app.application.services.stock_movement import StockMovementService
from app.application.dtos.stock_movement.stock_for_create import StockCreate

from app.application.dtos.wine.wine_for_view import WineRead
from app.application.dtos.wine.wine_for_update import WineUpdate
from app.application.dtos.wine.wine_for_create import WineCreate
from app.application.dtos.location.location_for_create import LocationForCreate



class WineNotFoundError(Exception):
    pass

class WineServiceError(Exception):
    pass

class WineServices:
    def __init__(self, session: AsyncSession, db: AsyncSession):
        self.repo = WineRepository(session)
        self.location_services = LocationServices(session)
        self.stock_movement_service = StockMovementService(session)
        self.stock_movement_repo = StockMovementRepository(session)
        self.db = db


    async def _transform_wine_to_read(self, wine: Wine,) -> WineRead:
        location = await self.location_services.get_by_code(wine.location_code)
        await self.db.refresh(wine, attribute_names=["location", "user"])
        return WineRead(
            name=wine.name,
            year=wine.year,
            grape=wine.grape,
            price_usd=wine.price_usd,
            stock=wine.stock,
            is_available=wine.is_available,
            location_name=wine.location.description,
            location_description=location.description if location else None,
            owner = (f"{wine.user.first_name} {wine.user.last_name}"if wine.user else "Unknown"),
            stock_status=(
                "Off stock" if wine.stock == 0 else
                "Low Stock" if wine.stock < 5 else
                "Good stock"
            )
        )

    async def list_wines(self, current_user:UserSession) -> List[WineRead]:
        try:
            if current_user.role != "admin":
                raise HTTPException(status_code=403,detail="you are not authorized to see all wines")
            wines = await self.repo.read(current_user.id)          
            return [await self._transform_wine_to_read(wine) for wine in wines]
        except Exception as e:
            raise WineServiceError(f"Error listing wine: {str(e)}")
    async def list_public_wines(self)-> List[WineRead]:
        
            wines = await self.repo.read() 
            if not wines:
                raise WineServiceError(f"Error listing wine")         
            return [await self._transform_wine_to_read(wine) for wine in wines]
        
    
    async def list_paginated_wines(self, current_user: UserSession, offset: int, limit: int) -> PaginatedWines:
        if current_user.role != "admin":
            raise HTTPException(status_code=403, detail="Not authorized")

        total = await self.repo.count_all(current_user.id)
        wines = await self.repo.paginated(current_user.id, offset=offset, limit=limit)
        items = [await self._transform_wine_to_read(wine) for wine in wines]

        return PaginatedWines(total=total, offset=offset, limit=limit, items=items)


    async def get_by_id(self, wine_id: int, current_user: UserSession ) -> Optional[WineRead]:
        try:
            if current_user.role != "admin":
                raise HTTPException(status_code=403,detail="you are not authorized to get a wine")
            wine = await self.repo.read_by_id(wine_id)
            print(wine)
            if not wine:
                raise WineNotFoundError(f"Wine with ID {wine_id} not found")
            
            return await self._transform_wine_to_read(wine)
        
        except Exception as e:
            raise WineServiceError(f"Error retrieving wine: {str(e)}")

    async def update(self, wine_id: int, wine_update: WineUpdate, current_user: UserSession) -> Optional[WineRead]:
        try:
            if current_user.role != "admin":
                raise HTTPException(status_code=403,detail="you are not authorized to change wines")
            wine = await self.repo.read_by_id_soft_delete(wine_id)
            if not wine:
                raise HTTPException(status_code=404, detail="Wine not found")
            
            update_data = wine_update.model_dump(exclude_unset=True)

            if wine_update.location_code is not None:
                location = await self.location_services.get_by_code(wine_update.location_code)
                if not location:
                    raise HTTPException(status_code=400, detail="Location not found for wine")

            for key, value in wine_update.model_dump(exclude_unset=True).items():
                setattr(wine, key, value)
            
            updated_wine = await self.repo.update(wine_id, wine)
           
            wine = await self._transform_wine_to_read(updated_wine)
            return WineRead.model_validate(wine)
            
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error updating wine: {str(e)}")
    
    async def create(self, wine_create: WineCreate) -> WineRead:
        try:
            
            if hasattr(wine_create, "location_code") and wine_create.location_code is not None:
                location = await self.location_services.get_by_code(wine_create.location_code)
             
                if not location:
                    location_create = LocationForCreate(
                        code=wine_create.location_code,
                        description=wine_create.location_description or ""
                    )
                    location = await self.location_services.create(location_create)

            if hasattr(wine_create, "stock") and wine_create.stock < 0:
                raise HTTPException(status_code=400, detail="Stock cannot be negative")

            wine = Wine(**wine_create.model_dump())
            wine = await self.repo.create(wine)

            if not wine:
                raise HTTPException(status_code=400, detail="Error creating wine")
            
            if wine.stock > 0:
                print("codigo importante", wine.stock, wine.id, wine.location_code)
                stock_movement = StockCreate(
                    delta=wine.stock,
                    wine_id=wine.id,
                    location_code=wine.location_code,
                    user_id=getattr(wine, "user_id", None)
                )
                await self.stock_movement_service.create(stock_movement)

            return await self._transform_wine_to_read(wine)
        except HTTPException:
            raise
        except IntegrityError:
            raise HTTPException(status_code=400, detail="Error of integrity, possibly a duplicate entry.")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error creating wine: {str(e)}")


    async def delete(self, wine_id: int, current_user: UserSession) -> JSONResponse:
        try:
            if current_user.role != "admin":
                raise HTTPException(status_code=403, detail="Only admin users can delete wines")

            wine = await self.repo.read_by_id(wine_id)
            if not wine:
                raise HTTPException(status_code=404, detail="Wine not found")
            
            if not wine.is_available:
                raise HTTPException(status_code=400, detail="Wine is already deleted")
            if wine.stock > 0:
                stock_movement = StockCreate(
                    delta=wine.stock,
                    wine_id=wine.id,
                    location_code=wine.location_code,
                    user_id=getattr(wine, "user_id", None)
                )
                await self.stock_movement_service.create(stock_movement)
            await self.repo.delete(wine)

            return JSONResponse(content={"message": f"Wine '{wine.name}' was successfully deleted."},status_code=200)
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error deleting wine: {str(e)}")

    async def set_stock(self, wine_id: int, stock_update: StockUpdate,current_user: UserSession) -> WineStockUpdate:
        if current_user.role != "admin":
            raise HTTPException(status_code=403, detail="Only admin users can update stock")
        if stock_update.stock < 0:
            raise HTTPException(status_code=400, detail="Stock can't be negative")       
        wine = await self.repo.set_stock(wine_id, stock_update.stock)
        if not wine:
            raise HTTPException(status_code=404, detail="Wine not found")
        
        return WineStockUpdate(stock=wine.stock)
