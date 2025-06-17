from fastapi import APIRouter, Depends, HTTPException
from typing import Annotated
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import Session

from app.application.dtos.user.user_credentials import Token
from app.application.services.user_service import UserService 
from app.persistence.configuration.database import get_db

class UserForAuthenticationRouter:
    router = APIRouter(prefix="/authenticate", tags=["authenticate"])

    @router.post("/login", status_code=200 ,response_model=Token)
    async def auth(
        credentials: Annotated[OAuth2PasswordRequestForm, Depends()],
       session: Session = Depends(get_db),
    ):
        service = UserService(session)
        user_auth = await service.authenticate_user(credentials.username, credentials.password)
        return user_auth.model_dump()