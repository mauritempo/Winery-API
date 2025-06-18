from typing import Optional, List
from fastapi import HTTPException
from sqlmodel import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.domain.entities.stock_movement import StockMovement

class StockMovementRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, movement: StockMovement) -> StockMovement:
        try:
            self.session.add(movement)
            await self.session.commit()
            await self.session.refresh(movement)
            return movement
        except Exception:
            await self.session.rollback()
            raise HTTPException(status_code=400, detail="Error creating stock movement")

    async def read(self) -> List[StockMovement]:
        statement = select(StockMovement)
        result = await self.session.execute(statement)
        return result.scalars().all()

    async def read_by_id(self, movement_id: int) -> Optional[StockMovement]:
        statement = select(StockMovement).where(StockMovement.id == movement_id)
        result = await self.session.execute(statement)
        return result.scalar_one_or_none()

    async def update(self, movement_id: int, movement_update: StockMovement) -> Optional[StockMovement]:
        movement = await self.read_by_id(movement_id)
        if not movement:
            raise HTTPException(status_code=404, detail="Stock movement not found")
        for key, value in movement_update.dict(exclude_unset=True).items():
            setattr(movement, key, value)
        await self.session.commit()
        await self.session.refresh(movement)
        return movement
