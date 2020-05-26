from pydantic import BaseModel
from typing import List

class SmevFile(BaseModel):
    id: str
    path: str

    class Config:
        orm_mode = True

class SmevMergeFile(BaseModel):
    ids: List[str]

class SmevFtpFile(BaseModel):
    user: str
    password: str
    path: str