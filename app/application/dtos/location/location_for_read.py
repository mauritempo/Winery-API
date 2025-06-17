from typing import Optional
from pydantic import BaseModel
from app.application.dtos.wine.wine_for_view import WineRead

class LocationForRead(BaseModel):
    code: str
    description: Optional[str] 
    wines: Optional[list[WineRead]] = None