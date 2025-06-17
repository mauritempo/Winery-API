from typing import Optional
from pydantic import BaseModel

class WineUpdate(BaseModel):

    name: Optional[str] = None
    grape: Optional[str]    = None
    price_usd: Optional[float]  = None
    year: Optional[int] = None
    stock: Optional[int]    = None
    is_available: Optional[bool] = None 
    location_code: str
