from pydantic import BaseModel

class SmevMesage(BaseModel):
    id: str
    xml: str