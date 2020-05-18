from sqlalchemy import Boolean, Column, Integer, String, Unicode, DateTime
from models.db import Base
from datetime import datetime

class Photo(Base):
    __tablename__ = "photos"
    id = Column(String, primary_key=True, index=True)
    path = Column(String, unique=True)
    approve_rate = Column(Integer, default=0)
    is_approved = Column(Boolean, default=False)
    annotation = Column(Unicode, default=None)
    date = Column(DateTime, default=datetime.now())
    label = Column(String, default=None)