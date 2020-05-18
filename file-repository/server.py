from fastapi import FastAPI, HTTPException, Request, File, UploadFile, Depends, Response
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from models.db import SessionLocal, engine
from models import db_models
from models import photo
from controllers import file_controller
from controllers import db_controller
import os
import json

# init
db_models.Base.metadata.create_all(bind=engine)

app = FastAPI()

def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()

# create file in repo
@app.post('/api/v1/photo/new')
async def create_file(file: UploadFile = File(...), db: Session = Depends(get_db)):
    try:
        if not await file_controller.is_image(file):
            raise Exception('is not image')

        id = await file_controller.calculate_id(file)
        if await db_controller.get_photo(db=db, id=id) != None:
            return { "id": id, "path": path }

        path = await file_controller.save_upload_file(file, id)
        
        p = photo.PhotoBase()
        p.id = id
        p.path = path
        await db_controller.create_photo(db=db, photo=p)

        return { "id": id, "path": path }
    except Exception as e:
        raise HTTPException(400, detail=str(e))

# get photo info
@app.get('/api/v1/photo/info/{id}')
async def create_file(id: str, db: Session = Depends(get_db)):
    p = await db_controller.get_photo(db=db, id=id)
    if p == None:
        raise HTTPException(404, detail="no such photo")
    return p

# change photo annotation
@app.post('/api/v1/photo/anno/{id}')
async def create_file(id: str, anno: photo.PhotoAnnotate, db: Session = Depends(get_db)):
    p = await db_controller.get_photo(db=db, id=id)
    if p == None:
        raise HTTPException(404, detail="no such photo")
    if anno.annotation == None and anno.label == None:
        raise HTTPException(400, "invalid annotation")

    anno.id = id
    if anno.annotation == None:
        anno.annotation = p.annotation
    if anno.label == None:
        anno.label = p.label
        
    return await db_controller.annotate_photo(db=db, photo=anno)

# get photo annotation in json format
@app.get('/api/v1/photo/anno/{id}')
async def create_file(id: str, db: Session = Depends(get_db)):
    try:
        p = await db_controller.get_photo(db=db, id=id)
        if p == None:
            raise HTTPException(404, detail="no such photo")
        if p.annotation == None:
            raise HTTPException(404, detail="photo has no annotation")
        return json.loads(p.annotation)
    except HTTPException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail, headers=e.headers)
    except Exception as e:
        raise HTTPException(500, detail="unable to parse annotation: {}".format(str(e)))

# get photo annotation in voc format
@app.get('/api/v1/photo/anno_voc/{id}')
async def create_file(id: str, db: Session = Depends(get_db)):
    p = await db_controller.get_photo(db=db, id=id)
    if p == None:
        raise HTTPException(404, detail="no such photo")
    raise HTTPException(404, detail="no inplement")

# change photo approve_rate
@app.get('/api/v1/photo/rate/{id}/{rate}')
async def create_file(id: str, rate: int, db: Session = Depends(get_db)):
    p = await db_controller.get_photo(db=db, id=id)
    if p == None:
        raise HTTPException(404, detail="no such photo")
    return await db_controller.change_photo_rate(db=db, id=id, approve_rate=rate)

# change photo approve status
@app.get('/api/v1/photo/approve/{id}')
async def create_file(id: str, approve: bool = False, db: Session = Depends(get_db)):
    p = await db_controller.get_photo(db=db, id=id)
    if p == None:
        raise HTTPException(404, detail="no such photo")
    return await db_controller.change_photo_approve_status(db=db, id=id, is_approved=approve)

# get photo data
@app.get('/api/v1/photo/data/{path}')
async def create_file(path: str):
    if not os.path.isfile(path):
        raise HTTPException(404, detail="no such photo")
    return FileResponse(path)