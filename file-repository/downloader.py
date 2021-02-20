import ftplib
import os
import shutil
import hashlib
from datetime import date
from io import BytesIO
from typing import List
import random

def get_file_from_ftp(path: str, host: str, user: str = 'anonimus', password: str = 'password'):
    with ftplib.FTP(host) as ftp:
        ftp.login(user=user, passwd=password)
        with open(os.path.basename(path), 'wb') as f:
            try:
                ftp.retrbinary('RETR %s' % path, f.write)
            except EOFError:
                pass

path = '/83b615bd-8bd9-40d9-b8a5-9202c450629f.zip.002'
user = 'G4Ci0A3oEgTJzRi1lcbjlp7U3ub5Y5'
password = 'vBDnx5xpcxLJxiOkl7IlSKJpxADSWX'
host = 'smev3-n0.test.gosuslugi.ru'

get_file_from_ftp(path=path, host=host, user=user, password=password)