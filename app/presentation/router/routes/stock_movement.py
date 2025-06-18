from fastapi import APIRouter, Depends
from typing import Annotated


class StockMovementRouter:
    router = APIRouter(prefix="/stock_movements", tags=["stock_movements"])

   
