from typing import List
from functools import lru_cache
from pydantic import BaseSettings

# https://github.com/tiangolo/fastapi/issues/508#issuecomment-532360198
class WorkerConfig(BaseSettings):
    project_name: str = "smev plugins api"
    api_prefix: str = "/v1/plugin"
    version: str = "1.0.0"
    openapi_url: str = "/docs/smev-plugins/openapi.json"
    docs_url: str = "/docs/smev-plugins/"
    debug: bool = False
    
    class Config:
        env_file = '.env'
        env_file_encoding = 'utf-8'

@lru_cache()
def get_config() -> WorkerConfig:
    return WorkerConfig()