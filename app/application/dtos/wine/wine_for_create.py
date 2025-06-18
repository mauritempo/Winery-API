from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, field_validator

class WineCreate(BaseModel):
    name: str = Field(..., example="Malbec Reserva")
    year: Optional[int] = Field(..., example="Malbec")
    grape: Optional[str] = Field(..., example=2021)
    price_usd: Optional[float] = Field(..., example=15.5)
    stock: int = Field(..., example=30)
    is_available: bool = Field(..., example=True)
    location_code: str = Field(..., example="A12")
    user_id: Optional[int] = Field(..., example=1)
    location_description: Optional[str] = Field(default="", example="shelf A aisle B")

    @field_validator("year")
    def validate_year(cls, v):
        current_year = datetime.now().year
        if v < 1900 or v > current_year:
            raise ValueError(f"Year must be between 1900 and {current_year}")
        return v