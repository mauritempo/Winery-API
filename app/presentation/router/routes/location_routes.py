from fastapi import APIRouter, Depends
from typing import Annotated


class LocationRouter:
    router = APIRouter(prefix="/locations", tags=["locations"])