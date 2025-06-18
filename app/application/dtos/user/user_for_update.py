from typing import Optional
from pydantic import BaseModel, Field
from app.domain.enum.user_role import UserRole

class UserForUpdate(BaseModel):
    username: Optional[str] = Field(None, example="newusername")
    last_name: Optional[str] = Field(None, example="González")
    role: Optional[UserRole] = Field(None, example="admin")
    is_active: Optional[bool] = Field(None, example=True)
    password: Optional[str] = Field(None, example="NewSecurePassword123")