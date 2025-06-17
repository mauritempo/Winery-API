from typing import Optional
from pydantic import BaseModel

class WineCreate(BaseModel):
    name: str
    year: Optional[int] = None
    grape: Optional[str] = None
    price_usd: Optional[float] = None
    stock: int
    is_available: bool
    location_code: str
    user_id: Optional[int]
    location_description: Optional[str] = ""