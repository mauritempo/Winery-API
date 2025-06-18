from typing import Optional
from pydantic import BaseModel, Field
from app.domain.enum.user_role import UserRole

class UserRead(BaseModel):
    id: int = Field( example=3)
    username: str = Field(example="juanperez")
    first_name: str = Field(example="Juan")
    last_name: str = Field(example="Pérez")
    is_active: bool = Field(example=True)
    role: str = Field(example="admin")
