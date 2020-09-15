from fastapi import FastAPI, HTTPException, Request, Response
import requests
from models.smev_mesage import SmevMesage
import lxml.etree as ET
import json
import re
import os
from datetime import datetime
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
    response = requests.post(host['url'], data=body, headers=headers, timeout=10)
    
    #RAW = host['url'] + '\n\tREQUEST POST\n' + body + '\n\tRESPONSE\n' + response.text
    #open(f'raw/{datetime.now()}.txt', 'w').write(RAW)
    
    response = response.content.decode('utf-8', errors='ignore')
    try:
        if 'soap:Envelope' in response:
            response = re.findall(r'<soap:Envelope[\s\S]*?</soap:Envelope>', response)[0]
        elif 'SOAP-ENV:Envelope' in response:
            response = re.findall(r'<SOAP-ENV:Envelope[\s\S]*?</SOAP-ENV:Envelope>', response)[0]
        else:
            raise Exception('no soap response')
        xml = ET.fromstring(response)
        xmlstr = ET.tostring(xml, encoding='utf-8').decode('utf-8')
        id = req.id
        try:
            id = re.findall(r'<ns[0-9]:OriginalMessageId>[0-9a-fA-F]{8}\-[0-9a-fA-F]{4}\-[0-9a-fA-F]{4}\-[0-9a-fA-F]{4}\-[0-9a-fA-F]{12}</ns[0-9]:OriginalMessageId>', xmlstr)[0]
            id = re.findall(r'[0-9a-fA-F]{8}\-[0-9a-fA-F]{4}\-[0-9a-fA-F]{4}\-[0-9a-fA-F]{4}\-[0-9a-fA-F]{12}', id)[0]
        except:
            id = req.id
        return SmevMesage(id=id, xml=xmlstr)
    except Exception as e:
        try:
            xml = ET.fromstring(response)
            response = ET.tostring(xml, encoding='utf-8').decode('utf-8')
        finally:
            raise HTTPException(400, f'invalid smev response {str(e)}: {response}')

# create file in repo
#@app.post('/api/v1/send/{smev_server}/xml')
async def send_mesage_raw(req: SmevMesage, smev_server: str):
    if(smev_hosts[smev_server] == None):
        raise HTTPException(400, f'no such smev host: {smev_server}')

    host = smev_hosts[smev_server]

    headers = {'content-type': 'text/xml'}
    body = req.xml
    response = requests.post(host['url'], data=body, headers=headers, timeout=10)
    response = response.content.decode('utf-8', errors='ignore')
    try:
        if 'soap:Envelope' in response:
            response = re.findall(r'<soap:Envelope[\s\S]*?</soap:Envelope>', response)[0]
        elif 'SOAP-ENV:Envelope' in response:
            response = re.findall(r'<SOAP-ENV:Envelope[\s\S]*?</SOAP-ENV:Envelope>', response)[0]
        else:
            raise Exception('no soap response')
        xml = ET.fromstring(response)
        xmlstr = ET.tostring(xml, encoding='utf-8').decode('utf-8')
        return Response(content=xmlstr, media_type="application/xml")
    except:
        try:
            xml = ET.fromstring(response)
            response = ET.tostring(xml, encoding='utf-8').decode('utf-8')
            return Response(content=response.content, media_type="application/xml")
        except:
            pass
    return Response(content=response.content, media_type="application/text")


@cron.interval_schedule(seconds=10)
def call_query_function():
    for smev_host in smev_hosts:
        try:
            # build GetResponseRequest
            print(f'alias: {smev_host}\n\tcontent: {smev_hosts[smev_host]}', flush=True)
            smev_host_name = smev_host
            smev_host = smev_hosts[smev_host]
            body = { "id": "0", "msgType": "GetResponseRequest", "tagForSign": "SIGNED_BY_CALLER" }
            headers = {'content-type': 'application/json'}
            host = f'http://localhost:5000/api/v1/message/{smev_host["signature"]}?type={str(smev_host["version"])}'
            response = requests.post(host, json=body, headers=headers, timeout=5)
            if response.status_code != 200:
                raise Exception('can not build GetResponseRequest mesage')

            # send request    
            body = response.json()
            body = body['xml']
            xmlstr_req = body
            headers = {'content-type': 'text/xml'}
            host = smev_host['url']
            response = requests.post(host, data=body, headers=headers, timeout=5)
            response = response.content.decode('utf-8', errors='ignore')
            try:
                if 'soap:Envelope' in response:
                    response = re.findall(r'<soap:Envelope[\s\S]*?</soap:Envelope>', response)[0]
                elif 'SOAP-ENV:Envelope' in response:
                    response = re.findall(r'<SOAP-ENV:Envelope[\s\S]*?</SOAP-ENV:Envelope>', response)[0]
                else:
                    raise Exception('no soap response')
                xml = ET.fromstring(response)
                xmlstr = ET.tostring(xml, encoding='utf-8').decode('utf-8')

                id = re.findall(r'<ns[0-9]:OriginalMessageId>[0-9a-fA-F]{8}\-[0-9a-fA-F]{4}\-[0-9a-fA-F]{4}\-[0-9a-fA-F]{4}\-[0-9a-fA-F]{12}</ns[0-9]:OriginalMessageId>', xmlstr)[0]
                id = re.findall(r'[0-9a-fA-F]{8}\-[0-9a-fA-F]{4}\-[0-9a-fA-F]{4}\-[0-9a-fA-F]{4}\-[0-9a-fA-F]{12}', id)[0]
                
                if not os.path.isdir('raw'):
                    os.mkdir('raw')
                if not os.path.isdir(os.path.join('raw', str(smev_host_name))):
                    os.mkdir(os.path.join('raw', str(smev_host_name)))

                with open(os.path.join('raw', str(smev_host_name), f'{id}-Response.xml'), 'w') as f:
                    f.write(xmlstr)

            except:
                if 'FAILURE' in response:
                    if not os.path.isdir('raw'):
                        os.mkdir('raw')
                    
                    if not os.path.isdir(os.path.join('raw', str(smev_host_name))):
                        os.mkdir(os.path.join('raw', str(smev_host_name)))
                    
                    time = str(datetime.now())
                    with open(os.path.join('raw', str(smev_host_name), f'error-Response.{time}.xml'), 'w') as f:
                        f.write(str(response))
                    with open(os.path.join('raw', str(smev_host_name), f'error-Request.{time}.xml'), 'w') as f:
                        f.write(xmlstr_req)

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
        except Exception as e:
            print(str(e), flush=True)
