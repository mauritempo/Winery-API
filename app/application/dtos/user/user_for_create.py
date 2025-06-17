from typing import Optional
from pydantic import BaseModel
from app.domain.enum.user_role import UserRole

class UserForCreate(BaseModel):
    username: str
    password: str
    first_name: str
    last_name: str
    role: UserRole