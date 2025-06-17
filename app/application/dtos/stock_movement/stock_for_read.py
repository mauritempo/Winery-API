from datetime import datetime
from typing import Optional
from pydantic import BaseModel

class StockMovementRead(BaseModel):
    id: int
    wine_id: int
    location_code: str
    timestamp: datetime
    comment: Optional[str] = ""
    delta: int
    user_id: int


