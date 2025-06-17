from sqlalchemy.exc import IntegrityError
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException

from app.application.dtos.user.user_credentials import UserSession
from app.domain.entities.wine import Wine
from app.persistence.repository.wine_repository import WineRepository
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
    def __init__(self, session: AsyncSession):
        self.repo = WineRepository(session)
        self.location_services = LocationServices(session)
        self.stock_movement_service = StockMovementService(session)


    async def _transform_wine_to_read(self, wine: Wine) -> WineRead:
        location = await self.location_services.get_by_code(wine.location_code)
        return WineRead(
            name=wine.name,
            year=wine.year,
            grape=wine.grape,
            price_usd=wine.price_usd,
            stock=wine.stock,
            is_available=wine.is_available,
            location_code=wine.location_code,
            location_description=location.description if location else None,
            user_id=wine.user_id,
            stock_status=(
                "Off stock" if wine.stock == 0 else
                "Low Stock" if wine.stock < 5 else
                "Good stock"
            )
        )

    async def list_wines(self, current_user:UserSession) -> List[WineRead]:
        try:
            if current_user.role != "admin":
                raise HTTPException(status_code=403,detail="No tienes permisos para ver todos los usuarios")
            wines = await self.repo.read(current_user.id)          
            return [await self._transform_wine_to_read(wine) for wine in wines]
        except Exception as e:
            raise WineServiceError(f"Error listing wine: {str(e)}")

    async def get_by_id(self, wine_id: int) -> Optional[WineRead]:
        try:
            wine = await self.repo.read_by_id(wine_id)
            if not wine:
                raise WineNotFoundError(f"Wine with ID {wine_id} not found")
            
            return await self._transform_wine_to_read(wine)
        
        except Exception as e:
            raise WineServiceError(f"Error retrieving wine: {str(e)}")

    async def update(self, wine_id: int, wine_update: WineUpdate) -> Optional[WineRead]:
        try:
            wine = await self.repo.read_by_id(wine_id)
            if not wine:
                raise HTTPException(status_code=404, detail="Vino no encontrado")

            if hasattr(wine_update, "location_code") and wine_update.location_code is not None:
                location = await self.location_services.get_by_code(wine_update.location_code)
                if not location:
                    raise HTTPException(status_code=400, detail="Location no encontrada para el vino.")

            if wine_update.stock is not None and wine_update.stock != wine.stock:
                if wine_update.stock < 0:
                    raise HTTPException(status_code=400, detail="stock can`t be negative")
                    
                delta = wine_update.stock - wine.stock
                stock_movement = StockCreate(
                    delta=delta,
                    wine_id=wine.id,
                    location_code=wine.location_code,
                    user_id=getattr(wine, "user_id", None)
                )
                await self.stock_movement_service.create(stock_movement)

            for key, value in wine_update.model_dump(exclude_unset=True).items():
                setattr(wine, key, value)
            
            updated_wine = await self.repo.update(wine_id, wine)
            wine = await self._transform_wine_to_read(wine)
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
        


    async def delete(self, wine_id: int) -> bool:
        try:
            wine = await self.repo.read_by_id(wine_id)
            if not wine:
                raise HTTPException(status_code=404, detail="Wine not found")

            if wine.stock > 0:
                stock_movement = StockCreate(
                    delta=-wine.stock,
                    wine_id=wine.id,
                    location_code=wine.location_code,
                    user_id=getattr(wine, "user_id", None)
                )
                await self.stock_movement_service.create(stock_movement)
            
            await self.repo.delete(wine)
            return True
            
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error deleting wine: {str(e)}")