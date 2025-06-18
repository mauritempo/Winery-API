from typing import Optional, List
from fastapi import HTTPException
from sqlmodel import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.domain.entities.location import Location

class LocationRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, location: Location) -> Location:
            self.session.add(location)
            print("guardadç¿", location)
            await self.session.commit()
            print("b", location)
            await self.session.refresh(location)
            print("a", location)
            return location
        
    async def read(self) -> List[Location]:
        statement = select(Location)
        result = await self.session.execute(statement)
        return result.scalars().all()
    
    async def read_by_code(self, code: str) -> Optional[Location]:
        statement = select(Location).where(Location.code == code)
        result = await self.session.execute(statement)
        return result.scalar_one_or_none()
    
    async def read_by_codes(self, codes: set[str]) -> List[Location]:
        stmt = select(Location).where(Location.code.in_(codes))
        result = await self.session.execute(stmt)
        return result.scalars().all()


    async def update(self, location_code: str, location_update: Location) -> Optional[Location]:
        location = await self.read_by_code(location_code)
        if not location:
            raise HTTPException(status_code=404, detail="Location not found")
        for key, value in location_update.dict(exclude_unset=True).items():
            setattr(location, key, value)
        await self.session.commit()
        await self.session.refresh(location)
        return location

    async def delete(self, location_code: str) -> Location:
        location = await self(location_code)
        if not location:
            raise HTTPException(status_code=404, detail="Location not found")
        await self.session.delete(location)
        await self.session.commit()
        return location
