from fastapi import APIRouter



from .user_routes import UserRouter
from .location_routes import LocationRouter 
from .stock_movement import StockMovementRouter
from .user_for_authentication import UserForAuthenticationRouter
from .wine_routes import router as WineRouter

class DashboardRouter:
    
    router = APIRouter(prefix="/api/dashboard", tags=["All endpoints"])

    @router.get("/healthcheck", summary="Health Check")
    async def healthcheck():
        return {"status": "ok", "message": "API is running smoothly"}

    @router.get("/info", summary="API Information")
    async def info():
        return {"info": "Dashboard API for winery management"}

    router.include_router(UserForAuthenticationRouter.router)
    router.include_router(UserRouter.router)
    router.include_router(WineRouter)
    # router.include_router(LocationRouter.router)
    # router.include_router(StockMovementRouter.router)

