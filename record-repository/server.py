from fastapi import FastAPI, HTTPException, Request, File, UploadFile, Depends, Response
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from models.db import SessionLocal, engine
from models import db_record
from models import record
from controllers import db_controller, xml_parser
import uuid
import os
import re
import json
import lxml.etree as ET

# init
db_record.Base.metadata.create_all(bind=engine)

app = FastAPI()

def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()

# create file in repo
@app.get('/api/v1/record/{id}/new')
async def create_record(id: str, db: Session = Depends(get_db)):
    db_msg = await db_controller.get_record(db=db, id=id)
    if db_msg != None:
        msg = record.Record().create_from_db(db_msg)
        return msg
        
    msg = record.Record()
    msg = msg.create(id=id)
    rec = await db_controller.create_record(db=db, record=msg)
    if rec != None:
        return msg
    else:
        raise HTTPException(500, detail='db error')

@app.get('/api/v1/records')
async def get_records(page: int = 0, size: int = 50, db: Session = Depends(get_db)):
    db_msgs = await db_controller.get_records(db=db, skip=page*size, limit=size)
    records = []
    for msg in db_msgs:
        records.append(record.Record().create_from_db(msg))
        
    return records

@app.get('/api/v1/records/worker')
async def get_records(page: int = 0, size: int = 50, db: Session = Depends(get_db)):
    db_msgs = await db_controller.get_worker_records(db=db, skip=page*size, limit=size)
    records = []
    for msg in db_msgs:
        r = record.WorkerRecord().create_from_db(msg)
        r.communication_type = xml_parser.get_communication_type(msg.get_request_response)
        records.append(r)
    return records

# get record info
@app.get('/api/v1/record/{id}')
async def get_record(id: str, db: Session = Depends(get_db)):
    rec = await db_controller.get_record(db=db, id=id)
    if rec == None:
        raise HTTPException(404, detail="no such record")
    return record.Record().create_from_db(rec=rec)

# get record info
@app.get('/api/v1/record/{id}/{mesage_type}')
async def get_record_content(id: str, mesage_type: str, db: Session = Depends(get_db)):
    rec = await db_controller.get_record(db=db, id=id)
    if rec == None:
        raise HTTPException(404, detail="no such record")
    
    result = None
    if mesage_type == 'GetRequestRequest':
        result = rec.get_request_request
    elif mesage_type == 'GetRequestResponse':
        result = rec.get_request_response
    elif mesage_type == 'GetResponseRequest':
        result = rec.get_response_request
    elif mesage_type == 'GetResponseResponse':
        result = rec.get_response_response

    elif mesage_type == 'SendRequestRequest':
        result = rec.send_request_request
    elif mesage_type == 'SendRequestResponse':
        result = rec.send_request_response
    elif mesage_type == 'SendResponseRequest':
        result = rec.send_response_request
    elif mesage_type == 'SendResponseResponse':
        result = rec.send_response_response

    elif mesage_type == 'AckRequest':
        result = rec.ack_request

    if result == None:
        raise HTTPException(404, detail="no such mesage in record")

    root = ET.fromstring(result)
    result = ET.tostring(root, encoding='utf-8')

    req_id = id
    try:
        id = re.findall(r'<ns[0-9]:OriginalMessageId>[0-9a-fA-F]{8}\-[0-9a-fA-F]{4}\-[0-9a-fA-F]{4}\-[0-9a-fA-F]{4}\-[0-9a-fA-F]{12}</ns[0-9]:OriginalMessageId>', result)[0]
        id = re.findall(r'[0-9a-fA-F]{8}\-[0-9a-fA-F]{4}\-[0-9a-fA-F]{4}\-[0-9a-fA-F]{4}\-[0-9a-fA-F]{12}', id)[0]
    except:
        id = req_id

    return {'id': id, 'xml': result }

# get record info
@app.put('/api/v1/record/{id}/{mesage_type}')
async def update_record_content(req: record.RecordUpdate, id: str, mesage_type: str, db: Session = Depends(get_db)):
    rec = await db_controller.get_record(db=db, id=id)
    if rec == None:
        raise HTTPException(404, detail="no such record")

    content = req.xml

    if mesage_type == 'GetRequestRequest':
        rec.get_request_request = content
    elif mesage_type == 'GetRequestResponse':
        rec.get_request_response = content
    elif mesage_type == 'GetResponseRequest':
        rec.get_response_request = content
    elif mesage_type == 'GetResponseResponse':
        rec.get_response_response = content

    elif mesage_type == 'SendRequestRequest':
        rec.send_request_request = content
    elif mesage_type == 'SendRequestResponse':
        rec.send_request_response = content
    elif mesage_type == 'SendResponseRequest':
        rec.send_response_request = content
    elif mesage_type == 'SendResponseResponse':
        rec.send_response_response = content

    elif mesage_type == 'AckRequest':
        rec.ack_request = content
    else:
        raise HTTPException(404, detail="invlid mesaage type")

    result = await db_controller.update_record(db=db, record=rec)

    if result == None:
        raise HTTPException(404, detail="no such mesage in record")

    return { 'updated_records': result }

# get record info
@app.put('/api/v1/record/{id}/{mesage_type}/xml')
async def update_record_content_xml(req: Request, id: str, mesage_type: str, db: Session = Depends(get_db)):
    rec = await db_controller.get_record(db=db, id=id)
    if rec == None:
        raise HTTPException(404, detail="no such record")

    content = await req.body()
    content = content.decode('utf-8')

    if mesage_type == 'GetRequestRequest':
        rec.get_request_request = content
    elif mesage_type == 'GetRequestResponse':
        rec.get_request_response = content
    elif mesage_type == 'GetResponseRequest':
        rec.get_response_request = content
    elif mesage_type == 'GetResponseResponse':
        rec.get_response_response = content

    elif mesage_type == 'SendRequestRequest':
        rec.send_request_request = content
    elif mesage_type == 'SendRequestResponse':
        rec.send_request_response = content
    elif mesage_type == 'SendResponseRequest':
        rec.send_response_request = content
    elif mesage_type == 'SendResponseResponse':
        rec.send_response_response = content

    elif mesage_type == 'AckRequest':
        rec.ack_request = content
    else:
        raise HTTPException(404, detail="invlid mesaage type")

    result = await db_controller.update_record(db=db, record=rec)

    if result == None:
        raise HTTPException(404, detail="no such mesage in record")

    return { 'updated_records': result }

# get record info
@app.get('/api/v1/record/{id}/{mesage_type}/xml')
async def get_record_content_xml(id: str, mesage_type: str, db: Session = Depends(get_db)):
    rec = await db_controller.get_record(db=db, id=id)
    if rec == None:
        raise HTTPException(404, detail="no such record")
    
    result = None
    if mesage_type == 'GetRequestRequest':
        result = rec.get_request_request
    elif mesage_type == 'GetRequestResponse':
        result = rec.get_request_response
    elif mesage_type == 'GetResponseRequest':
        result = rec.get_response_request
    elif mesage_type == 'GetResponseResponse':
        result = rec.get_response_response

    elif mesage_type == 'SendRequestRequest':
        result = rec.send_request_request
    elif mesage_type == 'SendRequestResponse':
        result = rec.send_request_response
    elif mesage_type == 'SendResponseRequest':
        result = rec.send_response_request
    elif mesage_type == 'SendResponseResponse':
        result = rec.send_response_response

    elif mesage_type == 'AckRequest':
        result = rec.ack_request

    if result == None:
        raise HTTPException(404, detail="no such mesage in record")

    root = ET.fromstring(result)
    result = ET.tostring(root, encoding='utf-8')

    return Response(content=result, media_type="application/xml")

# get record id
@app.get('/api/v1/record/{id}/{mesage_type}/id')
async def get_record_content_id(id: str, mesage_type: str, db: Session = Depends(get_db)):
    rec = await db_controller.get_record(db=db, id=id)
    if rec == None:
        raise HTTPException(404, detail="no such record")
    
    result = None
    if mesage_type == 'GetRequestRequest':
        result = rec.get_request_request
    elif mesage_type == 'GetRequestResponse':
        result = rec.get_request_response
    elif mesage_type == 'GetResponseRequest':
        result = rec.get_response_request
    elif mesage_type == 'GetResponseResponse':
        result = rec.get_response_response

    elif mesage_type == 'SendRequestRequest':
        result = rec.send_request_request
    elif mesage_type == 'SendRequestResponse':
        result = rec.send_request_response
    elif mesage_type == 'SendResponseRequest':
        result = rec.send_response_request
    elif mesage_type == 'SendResponseResponse':
        result = rec.send_response_response

    elif mesage_type == 'AckRequest':
        result = rec.ack_request

    if result == None:
        raise HTTPException(404, detail="no such mesage in record")

    root = ET.fromstring(result)
    result = ET.tostring(root, encoding='utf-8')
    id = ""
    try:
        id = re.findall(r'<ns[0-9]:MessageId>[0-9a-fA-F]{8}\-[0-9a-fA-F]{4}\-[0-9a-fA-F]{4}\-[0-9a-fA-F]{4}\-[0-9a-fA-F]{12}</ns[0-9]:MessageId>', result)[0]
        id = re.findall(r'[0-9a-fA-F]{8}\-[0-9a-fA-F]{4}\-[0-9a-fA-F]{4}\-[0-9a-fA-F]{4}\-[0-9a-fA-F]{12}', id)[0]
    except:
        raise HTTPException(404, detail="MessageId is not found")
    return {'id': id}

# get record id
@app.get('/api/v1/record/{id}/{mesage_type}/tfp_attachment')
async def get_record_content_attachment(id: str, mesage_type: str, db: Session = Depends(get_db)):
    rec = await db_controller.get_record(db=db, id=id)
    if rec == None:
        raise HTTPException(404, detail="no such record")
    
    result = None
    if mesage_type == 'GetRequestRequest':
        raise HTTPException(404, detail="GetRequestRequest have no attachment")
    elif mesage_type == 'GetRequestResponse':
        result = rec.get_request_response
    elif mesage_type == 'GetResponseRequest':
        raise HTTPException(404, detail="no attachment")
    elif mesage_type == 'GetResponseResponse':
        result = rec.get_response_response

    elif mesage_type == 'SendRequestRequest':
        raise HTTPException(404, detail="no attachment")
    elif mesage_type == 'SendRequestResponse':
        result = rec.send_request_response
    elif mesage_type == 'SendResponseRequest':
        raise HTTPException(404, detail="no attachment")
    elif mesage_type == 'SendResponseResponse':
        result = rec.send_response_response

    elif mesage_type == 'AckRequest':
        raise HTTPException(404, detail="no attachment")

    if result == None:
        raise HTTPException(404, detail="no such mesage in record")

    root = ET.fromstring(result)
    result = ET.tostring(root, encoding='utf-8')
    path = None
    user = None
    password = None
    try:
        user = re.findall(r'<UserName>[\s\S]*?</UserName>', result)[0]
        user = user.replace('<UserName>', '', 1)
        user = user.replace('</UserName>', '', 1)
        
        password = re.findall(r'<Password>[\s\S]*?</Password>', result)[0]
        password = password.replace('<Password>', '', 1)
        password = password.replace('</Password>', '', 1)

        path = re.findall(r'<FileName>[\s\S]*?</FileName>', result)[0]
        path = path.replace('<FileName>', '', 1)
        path = path.replace('</FileName>', '', 1)
    except:
        raise HTTPException(404, detail="Attacnment info is not found")
    return { 'user': user, 'password': password, 'path': path }

@app.delete('/api/v1/record/{id}')
async def remove_record(id: str, req: Request, db: Session = Depends(get_db)):
    rec = await db_controller.get_record(db=db, id=id)
    if rec == None:
        raise HTTPException(404, detail="no such record")
    
    result = await db_controller.remove_record(db=db, id=id)

    if result == None:
        raise HTTPException(404, detail="no such mesage in record")

    return { 'remove_records': result }
