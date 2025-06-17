from datetime import datetime, timedelta, timezone
from fastapi import HTTPException
import jwt
from dotenv import load_dotenv
import os
from passlib.context import CryptContext
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError



from app.application.dtos.user.user_for_view import UserRead
from app.application.dtos.user.user_for_create import UserForCreate
from app.application.dtos.user.user_for_update import UserForUpdate
from app.application.dtos.user.user_credentials import Token, UserSession
from app.persistence.repository.user_repository import UserRepository
from app.domain.entities.user import User


class UserService:
    def __init__(self, session: AsyncSession):
        self.repo = UserRepository(session)
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        load_dotenv()

    async def list_users(self, current_user: UserSession) -> list[UserRead]:
        try:
            if current_user.role != "admin":
                raise HTTPException(status_code=403, detail="No tienes permisos para ver todos los usuarios")
            
            users = await self.repo.read()
            return [UserRead.model_validate(user.model_dump()) for user in users]
        
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error al obtener usuarios: {str(e)}")
        
    # ,current_user: UserSession
    # if current_user.role == "admin" and current_user.role != "admin":
    #             raise HTTPException(
    #                 status_code=403,
    #                 detail="Only admin users can update roles"
    #             )
    async def create_user(self, user_create: UserForCreate ) -> UserRead:
        try:
            user_data = user_create.model_dump()
            user_data["hashed_password"] = self.pwd_context.hash(user_data.pop("password"))
            user = User(**user_data)
            user = await self.repo.create(user)
            return UserRead.model_validate(user.model_dump())
        except IntegrityError:
            raise HTTPException(status_code=409,detail="username exist or is desactivated")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error creating user: {str(e)}")

    async def update_user(self, user_id: int, user_update: UserForUpdate, current_user: UserSession) -> UserRead:
        try:
            if user_update.role == "admin" and current_user.role != "admin":
                raise HTTPException(status_code=403,detail="Only admin users can update roles")

            user = await self.repo.read_by_id(user_id)
            if not user:
                raise HTTPException(status_code=404,detail="User not found")

            for key, value in user_update.model_dump(exclude_unset=True).items():
                if key == "password":
                    setattr(user, "hashed_password", self.pwd_context.hash(value))
                else:
                    setattr(user, key, value)
            
            updated_user = await self.repo.update(user)
            return UserRead.model_validate(updated_user.model_dump())
        
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error updating user: {str(e)}")

    async def get_user_by_id(self, user_id: int, current_user: UserSession) -> UserRead:
        print("entrando al servicio")
        try:
            if current_user.role != "admin" and current_user.id != user_id:
                raise HTTPException(
                    status_code=403, 
                    detail="Acces denied, you only can see your profile"
                )
            user = await self.repo.read_by_id(user_id)

            if not user:
                raise HTTPException(status_code=404, detail="User not found")
            
            return UserRead.model_validate(user.model_dump())
        
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error getting user: {str(e)}")

    async def delete_user(self, user_id: int, current_user: UserSession) -> bool:

        try:
            if current_user.role != "admin":
                raise HTTPException(status_code=403,detail="Only admin users can update roles")

            user = await self.repo.read_by_id(user_id)
            if not user:
                raise HTTPException(status_code=404,detail="user not found")
            
            await self.repo.delete(user)
            return True
        
        except HTTPException as e:
            raise e
        except Exception as e:
            raise HTTPException(status_code=500,detail=f"error deleting user: {str(e)}")

    async def authenticate_user(self, username: str, password: str) -> Token:
        try:
            user = await self.repo.auth(username)

            if not user or not self.pwd_context.verify(password, user.hashed_password):
                raise HTTPException(
                    status_code=401,
                    detail="credentials invalid"
                )

            payload = {
                "sub": user.username,
                "id": user.id,
                "username": user.username,
                "role": user.role.value if hasattr(user.role, "value") else user.role,
                "exp": datetime.now(timezone.utc) + timedelta(hours=1)  
            }
            if not user.is_active:
                raise HTTPException(
                    status_code=401, 
                    detail="Acces denied: account desactivated"
                )
            
            secret_key = os.getenv("SECRET_KEY")
            if not secret_key:
                raise HTTPException(
                    status_code=500,
                    detail="SECRET_KEY not configured"
                )        
            token = jwt.encode(payload, secret_key, algorithm=os.getenv("HASH_ALGORITHM", "HS256"))
            return Token(access_token=token, token_type="bearer")
        
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500,detail=f"Error authenticating user: {str(e)}")