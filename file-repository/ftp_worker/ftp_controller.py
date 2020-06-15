import ftplib
import os
import shutil
import hashlib
from datetime import date
from io import BytesIO
from typing import List
import random
STORAGE = os.environ['STORAGE']

def get_file_from_ftp(path: str, host: str, user: str = 'anonimus', password: str = 'password'):
    
    hash_object = hashlib.sha1(bytes([random.randrange(0, 256) for _ in range(0, 2024)]))
    id = hash_object.hexdigest()
    time_path = os.path.join(STORAGE, str(date.today()))
    full_path = os.path.join(time_path, f'{id}.{os.path.basename(path)}')

    if not os.path.isdir(time_path):
            os.mkdir(time_path)

    with ftplib.FTP(host) as ftp:
        ftp.login(user=user, passwd=password)
        with open(full_path, 'wb') as f:
            ftp.retrbinary('RETR %s' % path, f.write)

    return id, full_path