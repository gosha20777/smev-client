from sqlalchemy import Boolean, Column, Integer, String, Unicode, DateTime
from models.db import Base
from datetime import datetime

class SmevFile(Base):
    __tablename__ = "files"
    __table_args__ = {'schema': 'smev3_client'}
    id = Column(String, primary_key=True, index=True)
    path = Column(String, unique=True)