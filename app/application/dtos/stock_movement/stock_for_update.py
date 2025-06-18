# app/application/dtos/wine/stock_update.py
from pydantic import BaseModel, Field

class StockUpdate(BaseModel):
    stock: int = Field(..., ge=0, description="New stock value. Must be >= 0")
