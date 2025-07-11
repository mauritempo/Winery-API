from datetime import datetime
from typing import Optional
from pydantic import BaseModel

class StockCreate(BaseModel):
    wine_id: int
    location_code: str
    delta: int
    user_id: int