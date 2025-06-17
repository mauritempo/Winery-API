from typing import Annotated
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
import os
from dotenv import load_dotenv

from app.persistence.repository.user_repository import UserRepository
from app.persistence.configuration.database import get_db
from app.application.dtos.user.user_credentials import UserSession

# Carga las variables de entorno
load_dotenv()

oauth2_bearer = OAuth2PasswordBearer(tokenUrl="/api/dashboard/authenticate/login")


async def current_user(
    token: Annotated[str, Depends(oauth2_bearer)],
    db=Depends(get_db),
) -> UserSession:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="No se pudo validar las credenciales",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(
            token,
            os.getenv("SECRET_KEY"),
            algorithms=[os.getenv("HASH_ALGORITHM", "HS256")]
        )
        username: str = payload.get("username")
        user_id: int = payload.get("id")
        user_role: str = payload.get("role")

        if username is None:
            raise credentials_exception
        
    except JWTError:
        raise credentials_exception

    
    # Busca el usuario en la base de datos
    repo = UserRepository(db)
    user = await repo.auth(username)

    if user is None:
        raise credentials_exception

    return UserSession(id=user_id, username=username, role=user_role)