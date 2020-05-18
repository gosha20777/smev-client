from fastapi import UploadFile
import os
import shutil
import hashlib
from datetime import date
import imghdr
from PIL import Image
from io import BytesIO

async def save_upload_file(upload_file: UploadFile, id: str):
    try:
        time_path = os.path.join('storage', str(date.today()))
        full_path = os.path.join(time_path, f'{id}.png')

        if not os.path.isdir(time_path):
            os.mkdir(time_path)
        
        await upload_file.seek(0)
        im = Image.open(BytesIO(await upload_file.read()))
        im.save(full_path, format="PNG")
    except Exception as e:
        raise Exception('unable to save file '+str(e))
    
    return full_path

async def calculate_id(upload_file: UploadFile):
    try:
        await upload_file.seek(0)
        hash_object = hashlib.sha1(await upload_file.read())
        hex_dig = hash_object.hexdigest()
    except Exception as e:
        raise Exception("unable to calculate hash " + str(e))
    return hex_dig

async def is_image(upload_file: UploadFile):
    try:
        await upload_file.seek(0)
        img_type = imghdr.what(BytesIO(await upload_file.read()))
        if img_type != 'png' and img_type != 'jpeg' and img_type != 'bmp':
            return False
        return True
    except Exception as e:
        raise Exception("unable to check image " + str(e))