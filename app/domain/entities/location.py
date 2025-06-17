from typing import List, Optional, TYPE_CHECKING
from sqlmodel import Relationship, SQLModel, Field
if TYPE_CHECKING:
    from app.domain.entities.wine import Wine
    from app.domain.entities.stock_movement import StockMovement

class Location(SQLModel, table=True):
    __tablename__ = "location"
    code: str = Field( primary_key=True)
    description: str

    wines: List["Wine"] = Relationship(back_populates="location")
    stock_movements: List["StockMovement"] = Relationship(back_populates="location")
    