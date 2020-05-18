from fastapi import FastAPI, HTTPException, Request, Response
import requests
from models.smev_mesage import SmevMesage
import lxml.etree as ET
import json
import re


def get_key(dict):
    return list(dict.keys()).pop()

smev_hosts = json.load(open('config.json', 'r'))

app = FastAPI()

# create file in repo
@app.post('/api/v1/send/{smev_server}')
async def send_mesage(req: SmevMesage, smev_server: str):
    if(smev_hosts[smev_server] == None):
        raise HTTPException(400, f'no such smev host: {smev_server}')

    host = smev_hosts[smev_server]

    headers = {'content-type': 'text/xml'}
    body = req.xml
    response = requests.post(host['url'], data=body, headers=headers, timeout=10)
    try:
        response = re.findall(r'<soap:Envelope[\s\S]*?</soap:Envelope>', response.content.decode('utf-8'))[0]
        xml = ET.fromstring(response)
        xmlstr = ET.tostring(xml, encoding='utf-8').decode('utf-8')
        return SmevMesage(id=req.id, xml=xmlstr)
    except Exception as e:
        raise HTTPException(400, f'invalid smev response: {str(e)}')

