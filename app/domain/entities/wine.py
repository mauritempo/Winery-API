from typing import Optional, List
from sqlmodel import SQLModel, Field, Relationship
from app.domain.entities.stock_movement import StockMovement
from app.domain.entities.user import User
from app.domain.entities.location import Location

class Wine(SQLModel, table=True):
    __tablename__ = "wine"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(nullable=False)
    grape: str = Field(nullable=False)
    year: int = Field(nullable=False)
    price_usd: float = Field(nullable=False)
    stock: int = Field(default=0, ge=0)
    is_available: bool = Field(default=True)

    user_id: int = Field(foreign_key="user.id")
    location_id: int = Field(foreign_key="location.id")

    user: Optional["User"] = Relationship(back_populates="wines")
    location: Optional["Location"] = Relationship(back_populates="wines")
    stock_movements: List["StockMovement"] = Relationship(back_populates="wine")