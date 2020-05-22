from fastapi import FastAPI, HTTPException, Request, Response
import requests
from models.smev_mesage import SmevMesage
import lxml.etree as ET
import json
import re
from apscheduler.scheduler import Scheduler

def get_key(dict):
    return list(dict.keys()).pop()

smev_hosts = json.load(open('config.json', 'r'))

app = FastAPI()

cron = Scheduler(daemon=True)
cron.start()

# create file in repo
@app.post('/api/v1/send/{smev_server}')
async def send_mesage(req: SmevMesage, smev_server: str):
    if(smev_hosts[smev_server] == None):
        raise HTTPException(400, f'no such smev host: {smev_server}')

    host = smev_hosts[smev_server]

    headers = {'content-type': 'text/xml'}
    body = req.xml
    #proxies = {
    #    "http": "http://192.168.110.33:3128",
    #    "https": "https://192.168.110.33:3128",
    #}
    #response = requests.post(host['url'], data=body, headers=headers, proxies=proxies, timeout=10)
    response = requests.post(host['url'], data=body, headers=headers, timeout=10)
    if response.status_code != 200:
        xml = ET.fromstring(response.content.decode('utf-8'))
        xmlstr = ET.tostring(xml, encoding='utf-8').decode('utf-8')
        raise HTTPException(400, f'invalid smev status_code: {response.status_code} : {xmlstr}')
    try:
        response = re.findall(r'<soap:Envelope[\s\S]*?</soap:Envelope>', response.content.decode('utf-8'))[0]
        xml = ET.fromstring(response)
        xmlstr = ET.tostring(xml, encoding='utf-8').decode('utf-8')
        id = req.id
        try:
            id = re.findall(r'<ns2:OriginalMessageId>[\s\S]*?</ns2:OriginalMessageId>', xmlstr)[0]
            id = re.findall(r'[0-9a-fA-F]{8}\-[0-9a-fA-F]{4}\-[0-9a-fA-F]{4}\-[0-9a-fA-F]{4}\-[0-9a-fA-F]{12}', id)[0]
        except:
            id = req.id
        return SmevMesage(id=id, xml=xmlstr)
    except Exception as e:
        raise HTTPException(400, f'invalid smev response: {str(e)}')

@cron.interval_schedule(seconds=20)
def call_query_function():
    # build GetResponseRequest
    body = { "id": "0", "msgType": "GetResponseRequest", "tagForSign": "SIGNED_BY_CALLER" }
    headers = {'content-type': 'application/json'}
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
    #proxies = {
    #    "http": "http://192.168.110.33:3128",
    #    "https": "https://192.168.110.33:3128",
    #}
    #response = requests.post(host, data=body, headers=headers, proxies=proxies, timeout=5)
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
    headers = {'content-type': 'application/json'}
    host = f'http://localhost:5002/api/v1/record/{id}/GetResponseRequest'
    response = requests.put(host, json=body, headers=headers, timeout=5)
    if response.status_code != 200:
        raise Exception(f'can not update GetResponseRequest mesage record: status code {response.status_code}')

    body = {  "xml": xmlstr }
    headers = {'content-type': 'application/json'}
    host = f'http://localhost:5002/api/v1/record/{id}/GetResponseResponse'
    response = requests.put(host, json=body, headers=headers, timeout=5)
    if response.status_code != 200:
        raise Exception(f'can not update GetResponseResponse mesage record: status code {response.status_code}')
