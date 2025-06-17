from typing import Optional, List
from fastapi import HTTPException
from sqlmodel import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.domain.entities.wine import Wine

class WineRepository:
    def __init__(self, session: AsyncSession):
        self.session: AsyncSession = session

    async def read_by_id(self, id: int) -> Optional[Wine]:
        statement = (
            select(Wine)
            .where(Wine.id == id)
            .where(Wine.is_available == True)
        )
        result = await self.session.execute(statement)
        return result.scalar_one_or_none()
    
    async def update(self, id: int, wine: Wine) -> Wine:
        existing_wine: Optional[Wine] = await self.read_by_id(id)
        if not existing_wine:
            raise HTTPException(status_code=404, detail="Wine not found")
        
        for key, value in wine.dict(exclude_unset=True).items():
            setattr(existing_wine, key, value)

        await self.session.commit()
        await self.session.refresh(existing_wine)
        return existing_wine

    async def read(self) -> List[Wine]:
        statement = select(Wine).where(Wine.is_available == True)
        result = await self.session.execute(statement)
        return result.scalars().all()
    
    async def read(self, user_id: Optional[int] = None) -> List[Wine]:
        stmt = select(Wine).where(Wine.is_available == True)
        if user_id is not None:
            stmt = stmt.where(Wine.user_id == user_id)
        result = await self.session.execute(stmt)
        return result.scalars().all()


    async def create(self, wine: Wine) -> Wine:
        try:
            self.session.add(wine)
            await self.session.commit()
            await self.session.refresh(wine)
            return wine
        except Exception:
            await self.session.rollback()
            raise HTTPException(status_code=400, detail="Error creating wine")

    async def delete(self, wine: Wine) -> Wine:
        wine.is_available = False
        self.session.add(wine)
        await self.session.commit()
        await self.session.refresh(wine)
        return wine
