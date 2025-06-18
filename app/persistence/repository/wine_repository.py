from typing import Optional, List
from fastapi import HTTPException
from sqlmodel import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from app.domain.entities.wine import Wine

class WineRepository:
    def __init__(self, session: AsyncSession):
        self.session: AsyncSession = session

    async def read_by_id(self, id: int) -> Optional[Wine]:
        statement = (select(Wine).where(Wine.id == id).where(Wine.is_available == True))
        result = await self.session.execute(statement)
        return result.scalar_one_or_none()
    async def read_by_id_soft_delete(self, id: int) -> Optional[Wine]:
        statement = (select(Wine).where(Wine.id == id))
        result = await self.session.execute(statement)
        return result.scalar_one_or_none()
    
    async def update(self, id: int, wine: Wine) -> Wine:
        existing_wine: Optional[Wine] = await self.read_by_id(id)
        for key, value in wine.model_dump(exclude_unset=True).items():
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
            self.session.add(wine)
            await self.session.commit()
            await self.session.refresh(wine)
            return wine
            

    async def delete(self, wine: Wine) -> Wine:
        wine.is_available = False
        wine.stock = 0
        self.session.add(wine)
        await self.session.commit()
        await self.session.refresh(wine)
        return wine

    async def count_all(self, user_id: Optional[int] = None) -> int:
        stmt = select(func.count()).select_from(Wine).where(Wine.is_available == True)
        if user_id:
            stmt = stmt.where(Wine.user_id == user_id)
        result = await self.session.execute(stmt)
        return result.scalar_one()
    
    async def paginated(self,user_id: Optional[int] = None,offset: int = 0,limit: int = 10) -> List[Wine]:
        stmt = select(Wine).where(Wine.is_available == True)
        if user_id:
            stmt = stmt.where(Wine.user_id == user_id)
        stmt = stmt.offset(offset).limit(limit)

        result = await self.session.execute(stmt)
        return result.scalars().all()
    
    async def set_stock(self, wine_id: int, new_stock: int) -> Wine:
        statement = select(Wine).where(Wine.id == wine_id)
        result = await self.session.execute(statement)
        wine = result.scalar_one_or_none()
        wine.stock = new_stock
        await self.session.commit()
        await self.session.refresh(wine)
        return wine
