from typing import Optional
from pydantic import BaseModel
from app.domain.enum.user_role import UserRole

class UserRead(BaseModel):

    username: str
    first_name: str
    last_name: str
    is_active: bool
    role: Optional[UserRole] 
