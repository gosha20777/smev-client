from fastapi import FastAPI, HTTPException, Request, File, UploadFile, Depends, Response
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from models.db import SessionLocal, engine
from models import db_smev_file
from models import smev_file
from controllers import file_controller
from controllers import db_controller
import worker
from redis import Redis
from rq import Queue, Worker
from rq.job import Job
import rq
import os
import base64
import json
import requests

# init
db_smev_file.Base.metadata.create_all(bind=engine)

resdis_connection = Redis(host='lacalhost', port=6379, db=0)
queue = Queue('ftp_queue', connection=resdis_connection)

app = FastAPI()

def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()

# create file in repo
@app.post('/api/v1/file/new')
async def create_file(file: UploadFile = File(...), db: Session = Depends(get_db)):
    try:
        id = await file_controller.calculate_id(file)
        f = await db_controller.get_file(db=db, id=id) 
        if f != None:
            return { "id": id, "path": f.path }

        path = await file_controller.save_upload_file(file, id)
        f = smev_file.SmevFile(id=id, path=path)
        return await db_controller.create_file(db=db, file=f)
    except Exception as e:
        raise HTTPException(400, detail=str(e))

# create file in repo
@app.post('/api/v1/file/merge')
async def merge_file(files: smev_file.SmevMergeFile, db: Session = Depends(get_db)):
    pathes = []
    for id in files.ids:
        f = await db_controller.get_file(db=db, id=id)
        if f == None:
            raise HTTPException(400, f"no such file {id}")
        pathes.append(f.path)
    id, path = await file_controller.megre_files(pathes)
    f = await db_controller.get_file(db=db, id=id) 
    if f != None:
        return { "id": id, "path": f.path }
    f = smev_file.SmevFile(id=id, path=path)
    return await db_controller.create_file(db=db, file=f)

# create file in repo
@app.post('/api/v1/file/from_smev')
async def get_file_from_smev(file: smev_file.SmevFtpFile, db: Session = Depends(get_db)):
    job = queue.enqueue(
            worker.get_file_from_ftp,
            file.path, file.user, file.password
        )
    return {'job': job.id}

@app.get('/api/v1/file/from_smev/{task_id}')
async def get_ftp_worker_result(task_id: str, db: Session = Depends(get_db)):
    try:     
        job = Job.fetch(task_id, connection=resdis_connection)
        if job.result is None:
            return {'status': job.get_status()}

        id, path = job.result
        f = smev_file.SmevFile(id=id, path=path)
        result = await db_controller.get_file(db=db, id=id)
        if result == None:
            result = await db_controller.create_file(db=db, file=f)
        return result
    except rq.exceptions.NoSuchJobError:
        return {'status': 'no such job'}
    except RuntimeError as ex:
        return {'error': ex}

# get photo info
@app.get('/api/v1/file/{id}')
async def get_file(id: str, db: Session = Depends(get_db)):
    f = await db_controller.get_file(db=db, id=id)
    if f == None:
        raise HTTPException(404, detail="no such file")
    return FileResponse(f.path, media_type='application/zip')

@app.get('/api/v1/file/{id}/attachment/{alias}')
async def get_attachment_from_file(id: str, alias: str, db: Session = Depends(get_db)):
    f = await db_controller.get_file(db=db, id=id)
    if f == None:
        raise HTTPException(404, detail="no such file")

    with open(f.path, "rb") as input_file:
        base64_string = base64.b64encode(input_file.read()).decode()
    
    # sign file
    host = f"http://localhost:5000/api/v1/pkcs7/{alias}"
    headers = {'content-type': 'application/text'}
    response = requests.post(host, data=base64_string, headers=headers, timeout=5)
    if response.status_code != 200:
        raise HTTPException(400, detail="cant sign file")
    result = {
		"fileName": os.path.basename(f.path),
		"mimeType": "application/zip",
		"signature": response.content.decode(),
		"content": base64_string
        }
    return result


# get photo info
@app.get('/api/v1/files')
async def get_files(page: int = 0, db: Session = Depends(get_db)):
    files = await db_controller.get_files(db=db, skip=50*page, limit=50)
    if files == None:
        raise HTTPException(404, detail="no files")
    return files
