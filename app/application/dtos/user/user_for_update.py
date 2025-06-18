from typing import Optional
from pydantic import BaseModel
from app.domain.enum.user_role import UserRole

class UserForUpdate(BaseModel):
    username: str
    last_name: str
    role: UserRole
    is_active: bool
    password: Optional[str]