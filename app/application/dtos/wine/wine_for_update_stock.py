from pydantic import BaseModel, Field

class WineStockUpdate(BaseModel):
    stock: int = Field(..., ge=0, description="New stock value. Must be >= 0")
