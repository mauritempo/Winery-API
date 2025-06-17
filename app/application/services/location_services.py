from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException
from app.domain.entities.location import Location
from app.application.dtos.location.location_for_read import LocationForRead
from app.application.dtos.location.location_for_create import LocationForCreate
from app.persistence.repository.location_repository import LocationRepository
from app.application.dtos.wine.wine_for_view import WineRead

class LocationServices:
    def __init__(self, session: AsyncSession):
        self.repo = LocationRepository(session)

    async def create(self, location_create: LocationForCreate) -> LocationForRead:
        location = Location(**location_create.model_dump())
        location = await self.repo.create(location)
        return LocationForRead(
            code=location.code,
            description=location.description,
            wines=[]
        )

    async def get_by_id(self, location_id: int) -> Optional[LocationForRead]:
        location = await self.repo.read_by_id(location_id)
        if not location:
            return None
        wines = [WineRead.model_validate(wine) for wine in getattr(location, "wines", [])] if hasattr(location, "wines") else []
        return LocationForRead(
            code=location.code,
            description=location.description,
            wines=wines
        )
    async def get_by_code(self, code: str) -> Optional[LocationForRead]:
        print("porno", code)
        location = await self.repo.read_by_code(code)
        print("loccc", location)
        if not location:
            return None  
        return LocationForRead(
            code=location.code,
            description=location.description,
        )
    
    async def get_by_codes(self, codes: set[str]) -> List[Location]:
        return await self.repo.read_by_codes(codes)


    async def list(self) -> List[LocationForRead]:
        locations = await self.repo.read()
        result = []
        for location in locations:
            wines = [WineRead.model_validate(wine) for wine in getattr(location, "wines", [])] if hasattr(location, "wines") else []
            result.append(LocationForRead(
                code=location.code,
                description=location.description,
                wines=wines
            ))
        return result

    async def delete(self, location__code: str) -> bool:
        location = await self.repo.read_by_code(location__code)
        if not location:
            raise HTTPException(status_code=404, detail="Location not found")
        # No permitir eliminar si tiene vinos asociados
        if hasattr(location, "wines") and location.wines and len(location.wines) > 0:
            raise HTTPException(status_code=400, detail="No se puede eliminar una location con vinos asociados.")
        await self.repo.delete(location__code)
        return True
    
