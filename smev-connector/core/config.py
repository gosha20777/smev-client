from typing import List
from starlette.config import Config
from starlette.datastructures import CommaSeparatedStrings, Secret

config = Config(".env")

PROJECT_NAME: str = config("PROJECT_NAME", default="App for conmmunication with smev")
API_PREFIX: str = config("API_PREFIX", default="/api/v1")
VERSION: str = config("API_PREFIX", default="0.0.0")
DEBUG: bool = config("DEBUG", cast=bool, default=False)

REDIS_HOST: str = config("API_PREFIX", default="redis")
STORAGE_PATH: str = config("API_PREFIX", default="storage")