from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException
from app.domain.entities.stock_movement import StockMovement
from app.application.dtos.stock_movement.stock_for_read import StockMovementRead
from app.application.dtos.stock_movement.stock_for_create import StockCreate
from app.persistence.repository.stock_movement_repository import StockMovementRepository

class StockMovementService:
    def __init__(self, session: AsyncSession):
        self.repo = StockMovementRepository(session)

    async def create(self, movement_create: StockCreate) -> StockMovementRead:
        movement = StockMovement(**movement_create.model_dump())
        movement = await self.repo.create(movement)
        return StockMovementRead.model_validate(movement.__dict__)

    async def get_by_id(self, movement_id: int) -> Optional[StockMovementRead]:
        movement = await self.repo.read_by_id(movement_id)
        if not movement:
            return None
        return StockMovementRead.model_validate(movement)

    async def list(self) -> List[StockMovementRead]:
        movements = await self.repo.read()
        return [StockMovementRead.model_validate(m) for m in movements]

    async def delete(self, movement_id: int) -> bool:
        movement = await self.repo.read_by_id(movement_id)
        if not movement:
            raise HTTPException(status_code=404, detail="Stock movement not found")
        await self.repo.delete(movement_id)
        return True