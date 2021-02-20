from sqlalchemy.orm import Session
from models import record, db_record
from typing import List

async def get_record(db: Session, id: str):
    return db.query(db_record.Record).filter(db_record.Record.id == id).first()

async def get_records(db: Session, skip: int = 0, limit: int = 100):
    return db.query(db_record.Record).offset(skip).limit(limit).all()

async def get_worker_records(db: Session, skip: int = 0, limit: int = 100):
    return db.query(db_record.Record).filter(db_record.Record.get_request_response != None).filter(db_record.Record.ack_request == None).offset(skip).limit(limit).all()

async def create_record(db: Session, record: record.Record):
    db_rec = db_record.Record(id=record.id, date=record.date)
    db.add(db_rec)
    db.commit()
    db.refresh(db_rec)
    return db_rec

async def update_record(db: Session, record: db_record.Record):
    rows = db.query(db_record.Record).filter(db_record.Record.id == record.id).update(
        {
            db_record.Record.get_request_request:   record.get_request_request,
            db_record.Record.get_request_response:  record.get_request_response,
            db_record.Record.get_response_request:  record.get_response_request,
            db_record.Record.get_response_response: record.get_response_response,

            db_record.Record.send_request_request:   record.send_request_request,
            db_record.Record.send_request_response:  record.send_request_response,
            db_record.Record.send_response_request:  record.send_response_request,
            db_record.Record.send_response_response: record.send_response_response,

            db_record.Record.ack_request: record.ack_request
        })
    db.commit()
    return rows

async def add_attachments_to_record(db: Session, record: db_record.Record, attachments: List[record.Attachment]):
    for a in attachments:
        can_add = True
        for s_a in record.attachments:
            if s_a.id == a.id:
                can_add = False
                break
        if not can_add:
            continue    
        new_a = db_record.Attachment(id=a.id, extension=a.extension)
        record.attachments.append(new_a)
        db.add(new_a)
    db.commit()
    return record.attachments.count()

async def remove_record(db: Session, id: str):
    rows = db.query(db_record.Record).filter(db_record.Record.id == id).delete()
    db.commit()
    return rows