from typing import Optional
from pydantic import BaseModel, Field
from app.domain.enum.user_role import UserRole

class UserForCreate(BaseModel):
    username: str = Field(..., example="juanperez")
    password: str = Field(..., example="SecurePass123")
    first_name: str = Field(..., example="Juan")
    last_name: str = Field(..., example="Pérez")
    role: UserRole = Field(..., example="user")