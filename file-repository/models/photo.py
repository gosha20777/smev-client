from pydantic import BaseModel
from datetime import datetime

class PhotoBase(BaseModel):
    id: str = ""
    path: str = ""

class PhotoAnnotate(PhotoBase):
    annotation: str = None
    label: str = None

class Photo(PhotoAnnotate):
    approve_rate: int
    is_approved: bool
    date: datetime

    class Config:
        orm_mode = True