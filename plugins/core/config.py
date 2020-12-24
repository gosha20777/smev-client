from typing import List
from functools import lru_cache
from pydantic import BaseSettings

# https://github.com/tiangolo/fastapi/issues/508#issuecomment-532360198
class WorkerConfig(BaseSettings):
    project_name: str = "smev plugins api"
    api_prefix: str = "/api/v1"
    version: str = "1.0.0"
    debug: bool = False

    core_api_url: str = "./snapshotes/lacmus-1-4.h5"
    class Config:
        env_file = '.env'
        env_file_encoding = 'utf-8'

@lru_cache()
def get_config() -> WorkerConfig:
    return WorkerConfig()