import ftplib
import os
import shutil
import hashlib
from datetime import date
from io import BytesIO
from typing import List
import random

def get_file_from_ftp(path: str, user: str = 'anonimus', password: str = 'password'):
    id, path = _get_file_from_ftp(path=path, host='smev3-n0.test.gosuslugi.ru', user=user, password=password)
    return id, path

def _get_file_from_ftp(path: str, host: str, user: str = 'anonimus', password: str = 'password'):
    
    hash_object = hashlib.sha1(bytes([random.randrange(0, 256) for _ in range(0, 2024)]))
    id = hash_object.hexdigest()
    time_path = os.path.join('storage', str(date.today()))
    full_path = os.path.join(time_path, f'{id}.{os.path.basename(path)}')

    if not os.path.isdir(time_path):
            os.mkdir(time_path)

    with ftplib.FTP(host) as ftp:
        ftp.login(user=user, passwd=password)
        with open(full_path, 'wb') as f:
            try:
                ftp.retrbinary('RETR %s' % path, f.write)
            except EOFError:
                pass

    return id, full_path