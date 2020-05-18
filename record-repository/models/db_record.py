from sqlalchemy import Boolean, Column, Integer, String, Unicode, DateTime
from models.db import Base
from datetime import datetime

class Record(Base):
    __tablename__ = "smev_records"
    id = Column(String, primary_key=True, index=True)
    date = Column(DateTime, default=datetime.now())
    get_request_request = Column(String)
    get_request_response = Column(String)
    get_response_request = Column(String)
    get_response_response = Column(String)
    send_request_request = Column(String)
    send_request_response = Column(String)
    send_response_request = Column(String)
    send_response_response = Column(String)
    ack_request = Column(String)
