from typing import Optional
from pydantic import BaseModel, Field

class WineUpdate(BaseModel):
    name: Optional[str] = Field(None, example="Cabernet Sauvignon")
    grape: Optional[str] = Field(None, example="Cabernet")
    price_usd: Optional[float] = Field(None, example=22.5)
    year: Optional[int] = Field(None, example=2019)
    is_available: Optional[bool] = Field(None, example=True)
    location_code: Optional[str] = Field(None,example="B05",description="Código de ubicación existente. Debe ser funcional (válido en el sistema).")
