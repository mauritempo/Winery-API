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
    location_code: str
    user_id: int
    stock_status: str
