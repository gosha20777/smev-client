import requests
from models.smev_mesage import SmevMesage
from models import xpath
import lxml.etree as ET
import json
import re


# build GetResponseRequest
body = { "id": "0", "msgType": "GetResponseRequest", "tagForSign": "SIGNED_BY_CALLER" }
headers = {'content-type': 'text/xml'}
host = 'http://localhost:5000/api/v1/isogd'
response = requests.post(host, json=body, headers=headers, timeout=5)
if response.status_code != 200:
    raise Exception('can not build GetResponseRequest mesage')

# send request    
body = response.json()
body = body['xml']
xmlstr_req = body
headers = {'content-type': 'text/xml'}
host = 'http://smev3-n0.test.gosuslugi.ru:7500/smev/v1.2/ws?wsd'
response = requests.post(host, data=body, headers=headers, timeout=5)
try:    
    response = re.findall(r'<soap:Envelope[\s\S]*?</soap:Envelope>', response.content.decode('utf-8'))[0]
    xml = ET.fromstring(response)
    xmlstr = ET.tostring(xml, encoding='utf-8').decode('utf-8')

    id = re.findall(r'<ns2:OriginalMessageId>[\s\S]*?</ns2:OriginalMessageId>', xmlstr)[0]
    id = re.findall(r'[0-9a-fA-F]{8}\-[0-9a-fA-F]{4}\-[0-9a-fA-F]{4}\-[0-9a-fA-F]{4}\-[0-9a-fA-F]{12}', id)[0]
except:
    raise Exception(f'wrong or empty smev responsse: {response}')

# update db record
body = {  "xml": xmlstr_req }
headers = {'content-type': 'text/xml'}
host = f'http://localhost:5002/api/v1/record/{id}/GetResponseRequest'
response = requests.put(host, json=body, headers=headers, timeout=5)
if response.status_code != 200:
    raise Exception(f'can not update GetResponseRequest mesage record: status code {response.status_code}')

body = {  "xml": xmlstr }
headers = {'content-type': 'text/xml'}
host = f'http://localhost:5002/api/v1/record/{id}/GetResponseResponse'
response = requests.post(host, json=body, headers=headers, timeout=5)
if response.status_code != 200:
    raise Exception(f'can not update GetResponseResponse mesage record: status code {response.status_code}')