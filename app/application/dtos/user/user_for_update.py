from typing import Optional
from pydantic import BaseModel
from app.domain.enum.user_role import UserRole

class UserForUpdate(BaseModel):
    username: Optional[str]
    last_name: Optional[str]
    role: Optional[UserRole]
    is_active: Optional[bool]
    password: Optional[str]