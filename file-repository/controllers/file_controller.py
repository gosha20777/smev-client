from fastapi import UploadFile
import os
import shutil
import hashlib
from datetime import date
from io import BytesIO
from typing import List
import random
STORAGE = os.environ['STORAGE']

async def save_upload_file(upload_file: UploadFile, id: str):
    try:
        time_path = os.path.join(STORAGE, str(date.today()))
        full_path = os.path.join(time_path, f'{id}.{upload_file.filename}')
        if not os.path.isdir(time_path):
            os.mkdir(time_path)
        
        await upload_file.seek(0)
        data = BytesIO(await upload_file.read())
        with open(full_path, 'wb') as f:
            shutil.copyfileobj(data, f)
        
        return full_path
    except Exception as e:
        raise Exception('unable to save file '+str(e))
    
    return full_path

async def megre_files(pathes: List[str]):
    if len(pathes) < 1:
        raise Exception('pathes list is empty')

    hash_object = hashlib.sha1(bytes([random.randrange(0, 256) for _ in range(0, 2024)]))
    id = hash_object.hexdigest()
    time_path = os.path.join(STORAGE, str(date.today()))
    full_path = os.path.join(time_path, f'{id}.{os.path.basename(pathes[0])}')

    if not os.path.isdir(time_path):
            os.mkdir(time_path)

    with open(full_path,'wb') as wfd:
        for f in pathes:
            with open(f,'rb') as fd:
                shutil.copyfileobj(fd, wfd)

    return id, full_path

async def calculate_id(upload_file: UploadFile):
    try:
        await upload_file.seek(0)
        hash_object = hashlib.sha1(await upload_file.read())
        hex_dig = hash_object.hexdigest()
    except Exception as e:
        raise Exception("unable to calculate hash " + str(e))
    return hex_dig

def get_digest(file_path):
    h = hashlib.sha1()

    with open(file_path, 'rb') as file:
        while True:
            # Reading is buffered, so we can read smaller chunks.
            chunk = file.read(h.block_size)
            if not chunk:
                break
            h.update(chunk)

    return h.hexdigest()