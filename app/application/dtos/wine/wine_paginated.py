from pydantic import BaseModel
from typing import List

from app.application.dtos.wine.wine_for_view import WineRead

class PaginatedWines(BaseModel):
    total: int
    offset: int
    limit: int
    items: List[WineRead]
