from typing import Optional, List
from sqlmodel import SQLModel, Field, Relationship
from app.domain.entities.wine import Wine
from app.domain.entities.stock_movement import StockMovement

class User(SQLModel, table=True):
    __tablename__ = "user"

    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(index=True, unique=True, nullable=False)
    hashed_password: str
    is_active: bool = Field(default=True)
    first_name: str
    last_name: str

    wines: List["Wine"] = Relationship(back_populates="user")
    stock_movements: List["StockMovement"] = Relationship(back_populates="user")