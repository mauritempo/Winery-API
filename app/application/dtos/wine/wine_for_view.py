from pydantic import BaseModel, Field
from typing import Optional

class WineRead(BaseModel):
    name: str = Field(..., example="Malbec Reserva")
    grape: str = Field(..., example="Malbec")
    price_usd: float = Field(..., example=15.5)
    year: int = Field(..., example=2021)
    stock: int = Field(..., example=30)
    is_available: bool = Field(..., example=True)
    location_description: Optional[str] = Field(None, example="Estante superior zona A")
    location_name: str = Field(..., example="A12")
    owner: str = Field(..., example="juanperez")
    stock_status: str = Field(..., example="Disponible")
