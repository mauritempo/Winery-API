from typing import Optional, List
from fastapi import HTTPException
from sqlmodel import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.domain.entities.user import User

class UserRepository:
    def __init__(self, session: AsyncSession):
        self.session = session


    async def auth(self, id: int) -> Optional[User]:
        statement = select(User).where(User.is_active == True).where(User.username == id)
        result = await self.session.execute(statement)
        return result.scalar_one_or_none()

    async def create(self, user: User) -> User:
        self.session.add(user)
        await self.session.commit()
        await self.session.refresh(user)
        return user
        
    async def read(self) -> List[User]:
        statement = select(User).where(User.is_active == True)
        result = await self.session.execute(statement)
        return result.scalars().all()

    async def read_by_id(self, user_id: int) -> Optional[User]:
        statement = select(User).where(User.is_active == True, User.id == user_id)
        result = await self.session.execute(statement)
        return result.scalar_one_or_none()

    async def update(self, user: User) -> Optional[User]:
        try:
            self.session.add(user)
            await self.session.commit()
            await self.session.refresh(user)
            return user
        except Exception:
            await self.session.rollback()

    async def delete(self, user: User) -> User:
        try:
            user.is_active = False
            self.session.add(user)
            await self.session.commit()
            await self.session.refresh(user)
            return user
        except Exception:
            await self.session.rollback()
            raise HTTPException(status_code=400, detail="Error deleting user")
