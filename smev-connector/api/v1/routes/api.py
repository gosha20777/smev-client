from fastapi import APIRouter
from api.v1.routes import smev_connect

router = APIRouter()

router.include_router(smev_connect.router, tags=["smev_connect"])