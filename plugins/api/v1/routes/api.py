from fastapi import APIRouter
from api.v1.routes import ping
from api.v1.routes import client
from api.v1.routes import worker
from api.v1.routes import ros_reestr

router = APIRouter()

router.include_router(ping.router, tags=["ping"])
router.include_router(client.router, tags=["client"])
router.include_router(worker.router, tags=["worker"])
router.include_router(ros_reestr.router, tags=["ros_reestr"])