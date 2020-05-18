from sqlalchemy.orm import Session
from models import photo, db_models

async def get_photo(db: Session, id: str):
    return db.query(db_models.Photo).filter(db_models.Photo.id == id).first()

async def get_photos(db: Session, skip: int = 0, limit: int = 100):
    return db.query(db_models.Photo).offset(skip).limit(limit).all()

async def annotate_photo(db: Session, photo: photo.PhotoAnnotate):
    rows = db.query(db_models.Photo).filter(db_models.Photo.id == photo.id).update(
        {
            db_models.Photo.annotation: photo.annotation,
            db_models.Photo.label: photo.label
        })
    db.commit()
    return db.query(db_models.Photo).filter(db_models.Photo.id == photo.id).first()

async def change_photo_rate(db: Session, id: str, approve_rate: int):
    rows = db.query(db_models.Photo).filter(db_models.Photo.id == id).update(
        {
            db_models.Photo.approve_rate: approve_rate
        })
    db.commit()
    return db.query(db_models.Photo).filter(db_models.Photo.id == photo.id).first()

async def change_photo_approve_status(db: Session, id: str, is_approved: bool):
    rows = db.query(db_models.Photo).filter(db_models.Photo.id == id).update(
        {
            db_models.Photo.is_approved: is_approved
        })
    db.commit()
    return db.query(db_models.Photo).filter(db_models.Photo.id == photo.id).first()

async def create_photo(db: Session, photo: photo.PhotoBase):
    db_photo = db_models.Photo(id=photo.id, path=photo.path)
    db.add(db_photo)
    db.commit()
    db.refresh(db_photo)
    return db_photo
    