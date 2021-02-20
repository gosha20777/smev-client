from sqlalchemy.orm import Session
from models import smev_file, db_smev_file

async def get_file(db: Session, id: str):
    return db.query(db_smev_file.SmevFile).filter(db_smev_file.SmevFile.id == id).first()

async def get_files(db: Session, skip: int = 0, limit: int = 100):
    return db.query(db_smev_file.SmevFile).offset(skip).limit(limit).all()

async def create_file(db: Session, file: smev_file.SmevFile):
    db_file = db_smev_file.SmevFile(id=file.id, path=file.path)
    db.add(db_file)
    db.commit()
    db.refresh(db_file)
    return db_file
    