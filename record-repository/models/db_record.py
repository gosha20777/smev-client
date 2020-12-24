from sqlalchemy import Boolean, Column, Integer, String, Unicode, DateTime, ForeignKey
from models.db import Base
from datetime import datetime
from sqlalchemy.orm import relationship
import os
schema = os.environ['POSTGRES_SCHEMA']

class Record(Base):
    __tablename__ = "smev_records"

    if schema != 'NULL':
        __table_args__ = {'schema': schema }
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
    if schema != 'NULL':
        attachments = relationship('Attachment', backref=f'{schema}.smev_records',
                                lazy='dynamic')
    elif:
        attachments = relationship('Attachment', backref='smev_records',
                                lazy='dynamic')

class Attachment(Base):
    __tablename__ = "smev_attachments"
    if schema != 'NULL':
        __table_args__ = {'schema': schema }
    id = Column(String, primary_key=True, index=True)
    extension = Column(String)
    if schema != 'NULL':
        record_id = Column(String, ForeignKey(f'{schema}.smev_records.id'))
    elif:
        record_id = Column(String, ForeignKey(f'smev_records.id'))