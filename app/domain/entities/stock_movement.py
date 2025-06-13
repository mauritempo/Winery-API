from typing import Optional
from datetime import datetime
from sqlmodel import SQLModel, Field, Relationship
from app.domain.entities.user import User
from app.domain.entities.wine import Wine
from app.domain.entities.location import Location

class StockMovement(SQLModel, table=True):
    __tablename__ = "stock_movement"

    
    id: Optional[int] = Field(default=None, primary_key=True)
    delta: int = Field(nullable=False)       
    timestamp: datetime
    comment: Optional[str] = None             
   
    wine_id: int = Field(foreign_key="wine.id")
    user_id: Optional[int] = Field(foreign_key="user.id")
    location_id: Optional[int] = Field(foreign_key="location.id")

    wine: Optional["Wine"] = Relationship(back_populates="stock_movements")
    user: Optional["User"] = Relationship(back_populates="stock_movements")
    location: Optional["Location"] = Relationship(back_populates="stock_movements")

