from pydantic import BaseModel
from typing import Optional

class WineRead(BaseModel):

    name: str
    grape: str
    price_usd: float
    year: int
    stock: int
    is_available: bool

    location_description: Optional[str]
    location_name: str 
    owner: str  
    stock_status: str
    
    class Config:
        orm_mode = True