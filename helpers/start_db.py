from sqlmodel import create_engine, SQLModel
from app.domain.entities.user import User
from app.domain.entities.wine import Wine
from app.domain.entities.location import Location
from app.domain.entities.stock_movement import StockMovement
import os

DATABASE_URL = os.getenv("DATABASE_URL").replace("+aiosqlite", "")

def start_db():
    sync_engine = create_engine(DATABASE_URL)
    SQLModel.metadata.create_all(
    bind=sync_engine,
    tables=[
        User.__table__,
        Wine.__table__,
        Location.__table__,
        StockMovement.__table__,
    ],
)
