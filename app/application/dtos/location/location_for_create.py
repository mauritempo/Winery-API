from typing import Optional
from pydantic import BaseModel

class LocationForCreate(BaseModel):
    code: str
    description: Optional[str] 