from sqlalchemy import Boolean, Column, Integer, String, Unicode, DateTime
from models.db import Base
from datetime import datetime
import os
schema = os.environ['POSTGRES_SCHEMA'] # smev3_client

class SmevFile(Base):
    __tablename__ = "files"
    if schema != 'NULL':
        __table_args__ = {'schema': schema}
    id = Column(String, primary_key=True, index=True)
    path = Column(String, unique=True)