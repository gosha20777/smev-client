from fastapi import FastAPI
from api.v1.routes.api import router as api_router
from core.config import get_config

def get_application() -> FastAPI:
    project_name = get_config().project_name
    debug = get_config().debug
    version = get_config().version
    prefix = get_config().api_prefix
    docs_url = get_config().docs_url
    openapi_url = get_config().openapi_url

    application = FastAPI(title=project_name,
        debug=debug,
        version=version,
        docs_url=docs_url,
        openapi_url=openapi_url)
    application.include_router(api_router, prefix=prefix)
    return application

app = get_application()