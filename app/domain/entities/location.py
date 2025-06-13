from typing import List, Optional
from sqlmodel import Relationship, SQLModel, Field
from app.domain.entities.wine import Wine
from app.domain.entities.stock_movement import StockMovement

class Location(SQLModel, table=True):
    __tablename__ = "location"
    id: Optional[int] = Field(default=None, primary_key=True)
    code: str 
    description: str

    wines: List["Wine"] = Relationship(back_populates="location")
    stock_movements: List["StockMovement"] = Relationship(back_populates="location")
    