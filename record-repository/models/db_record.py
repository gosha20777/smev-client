from sqlalchemy import Boolean, Column, Integer, String, Unicode, DateTime, ForeignKey
from models.db import Base
from datetime import datetime
from sqlalchemy.orm import relationship

class Record(Base):
    __tablename__ = "smev_records"
    __table_args__ = {'schema': 'smev3_client'}
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
    attachments = relationship('Attachment', backref='smev_records',
                                lazy='dynamic')

class Attachment(Base):
    __tablename__ = "smev_attachments"
    __table_args__ = {'schema': 'smev3_client'}
    id = Column(String, primary_key=True, index=True)
    extension = Column(String)
    record_id = Column(String, ForeignKey('smev_records.id'))