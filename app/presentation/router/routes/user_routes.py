from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from pydantic import ValidationError
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from app.persistence.configuration.database import get_db
from app.application.services.user_service import UserService
from app.application.dtos.user.user_for_view import UserRead
from app.application.dtos.user.user_for_create import UserForCreate
from app.application.dtos.user.user_for_update import UserForUpdate
from app.application.dtos.user.user_credentials import UserSession
from helpers.auth_user import current_user  
class UserRouter:
    router = APIRouter(prefix="/users", tags=["users"])

    def get_user_service(db: AsyncSession = Depends(get_db)):
        return UserService(db)

    @router.get("/", response_model=List[UserRead])
    async def list_users(
        service: UserService = Depends(get_user_service),
        current_user: UserSession = Depends(current_user)
        ):  
        try:
            users = await service.list_users(current_user)
            return users
        except ValidationError as e:
            raise HTTPException(status_code=422, detail=f"Error de validación: {e.errors()}")

    @router.get("/{user_id}", response_model=UserSession)
    async def get_user(
        user_id: int,
        service: UserService = Depends(get_user_service),
        current_user: UserSession = Depends(current_user)
        ):

        user = await service.get_user_by_id(user_id, current_user)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return user
    
# response_model=UserSession
# current_user: UserSession = Depends(current_user)
    @router.post("/", status_code=status.HTTP_201_CREATED)
    async def create_user(
        user: UserForCreate,
        service: UserService = Depends(get_user_service),
        ):
        return await service.create_user(user)

    @router.put("/{user_id}", response_model=UserSession)
    async def update_user(
        user_id: int,
        user_update: UserForUpdate,
        service: UserService = Depends(get_user_service),
        current_user: UserSession = Depends(current_user)
        ):

        updated = await service.update_user(user_id, user_update,current_user)
        return updated

    @router.delete("/{user_id}", status_code=status.HTTP_200_OK)
    async def delete_user(
        user_id: int,
        service: UserService = Depends(get_user_service),
        current_user: UserSession = Depends(current_user),  
        ):
        await service.delete_user(user_id, current_user)
        return JSONResponse(content={"message": f"User with ID {user_id} was successfully deleted."}, status_code=200)
        