from fastapi import FastAPI
from .router.routes.api_dashboard import DashboardRouter
from helpers.start_db import start_db
from fastapi import Request
from fastapi.responses import JSONResponse


start_db() 
app = FastAPI(title="Vinoteca Dashboard API")
app.include_router(DashboardRouter.router)

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )

