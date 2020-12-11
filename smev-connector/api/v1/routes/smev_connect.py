from fastapi import APIRouter, HTTPException, Request, Response
from apscheduler.scheduler import Scheduler
from datetime import datetime
import lxml.etree as ET
import requests
import json
import re
import os

from core.models.record import SmevMesage
from core.helpers.dict_ops import pop_key
from core.helpers import mtom_reader as mtom

router = APIRouter()
# TODO: configure path 
json_config_path = 'configs/config-v1.0.json'
smev_hosts = json.load(open(json_config_path, 'r'))
cron = Scheduler(daemon=True)
cron.start()

# TODO: 
# - remove duplicate code
# - debug mode

@router.get("/probe")
async def root():
    return {"message": "API version 1.0"}

@router.post('/send/{smev_server}')
async def send_mesage(req: SmevMesage, smev_server: str):
    if(smev_hosts[smev_server] == None):
        raise HTTPException(400, f'no such smev host: {smev_server}')

    host = smev_hosts[smev_server]

    headers = {'content-type': 'text/xml; charset=utf-8'}
    body = req.xml
    response = requests.post(host['url'], data=body.encode('utf-8'), headers=headers, timeout=10)
    
    # TODO: if debug:
    # RAW = host['url'] + '\n\tREQUEST POST\n' + body + '\n\tRESPONSE\n' + response.text
    # open(f'raw/{datetime.now()}.txt', 'w').write(RAW)
    
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

@router.post('/send/{smev_server}/xml')
async def send_mesage_raw(req: SmevMesage, smev_server: str):
    if(smev_hosts[smev_server] == None):
        raise HTTPException(400, f'no such smev host: {smev_server}')

    host = smev_hosts[smev_server]

    headers = {'content-type': 'text/xml; charset=utf-8'}
    body = req.xml
    response = requests.post(host['url'], data=body.encode('utf-8'), headers=headers, timeout=10)
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

@cron.interval_schedule(seconds=15)
def call_smev_queues():
    for smev_host in smev_hosts:
        print(f'client alias: {smev_host}', flush=True)
        smev_host_name = smev_host
        smev_host = smev_hosts[smev_host]
        for queue in smev_host['client_signatures']:
            try:
                print(f'\tclient signature: {queue}')
                # build GetResponseRequest
                body = { "id": "0", "msgType": "GetResponseRequest", "tagForSign": "SIGNED_BY_CALLER" }
                headers = {'content-type': 'application/json'}
                host = f'{smev_host["signer_url"]}/message/{queue}?type={str(smev_host["version"])}'
                response = requests.post(host, json=body, headers=headers, timeout=5)
                if response.status_code != 200:
                    raise Exception('can not build GetResponseRequest mesage')

                # send request to smev   
                body = response.json()
                body = body['xml']
                xmlstr_req = body
                headers = {'content-type': 'text/xml'}
                host = smev_host['url']
                raw_response = requests.post(host, data=body, headers=headers, timeout=10)
                response = raw_response.content.decode('utf-8', errors='ignore')
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

                    # read mtom
                    mtom_ids: list = []
                    mtom_ids_dict = mtom.get_mtom_attachments_ids(xmlstr)
                    if len(mtom_ids_dict.keys()) > 0:
                        mtom_files = mtom.get_mtom_files(raw_response, mtom_ids_dict)
                        for mtom_file in mtom_files.keys():
                            print(mtom_file)

                            multipart_form_data = {
                                'file': (mtom_file, mtom_files[mtom_file])
                            }
                            host = f'http://localhost:6504/api/v1/file/new'
                            response = requests.post(host, files=multipart_form_data, timeout=5)
                            if response.status_code == 200:
                                f_id = response.json()
                                f_meta = {
                                    "id": f_id['id'],
                                    "extension": f_id['path'].split(".")[-1]
                                }
                                mtom_ids.append(f_meta)
                                print(f"get mtom id: {f_id['id']}")
                
                    if not os.path.isdir('raw'):
                        os.mkdir('raw')
                    if not os.path.isdir(os.path.join('raw', str(smev_host_name))):
                        os.mkdir(os.path.join('raw', str(smev_host_name)))
                    if not os.path.isdir(os.path.join('raw', str(smev_host_name), 'client')):
                        os.mkdir(os.path.join('raw', str(smev_host_name), 'client'))
                    if not os.path.isdir(os.path.join('raw', str(smev_host_name), 'client', queue)):
                        os.mkdir(os.path.join('raw', str(smev_host_name), 'client', queue))
                    
                    with open(os.path.join('raw', str(smev_host_name), 'client', queue, f'{id}-Response.xml'), 'wb') as f:
                        f.write(raw_response)

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
                        raise Exception(f'\tclient wrong smev responsse: {response}')
                    raise Exception(f'\tclient empty smev responsse')

                # update db record
                body = {  "xml": xmlstr_req }
                headers = {'content-type': 'application/json'}
                host = f'http://localhost:6502/api/v1/record/{id}/GetResponseRequest'
                response = requests.put(host, json=body, headers=headers, timeout=5)
                if response.status_code != 200:
                    raise Exception(f'can not update GetResponseRequest mesage record: status code {response.status_code}')

                body = {  "xml": xmlstr, "mtoms": mtom_ids }
                headers = {'content-type': 'application/json'}
                host = f'http://localhost:6502/api/v1/record/{id}/GetResponseResponse'
                response = requests.put(host, json=body, headers=headers, timeout=5)
                if response.status_code != 200:
                    raise Exception(f'can not update GetResponseResponse mesage record: status code {response.status_code}')
                print(f'\tclient create new record {id}')
            except Exception as e:
                print(str(e), flush=True)
        
        for queue in smev_host['worker_signatures']:
            try:
                print(f'\tworker signature: {queue}')
                # build GetRequestRequest
                body = { "id": "0", "msgType": "GetRequestRequest", "tagForSign": "SIGNED_BY_CALLER" }
                headers = {'content-type': 'application/json'}
                host = f'{smev_host["signer_url"]}/message/{queue}?type={str(smev_host["version"])}'
                response = requests.post(host, json=body, headers=headers, timeout=5)
                if response.status_code != 200:
                    raise Exception('can not build GetRequestRequest mesage')

                # send request to smev   
                body = response.json()
                body = body['xml']
                xmlstr_req = body
                headers = {'content-type': 'text/xml'}
                host = smev_host['url']
                raw_response = requests.post(host, data=body, headers=headers, timeout=10)
                response = raw_response.content.decode('utf-8', errors='ignore')
                try:
                    if 'soap:Envelope' in response:
                        response = re.findall(r'<soap:Envelope[\s\S]*?</soap:Envelope>', response)[0]
                    elif 'SOAP-ENV:Envelope' in response:
                        response = re.findall(r'<SOAP-ENV:Envelope[\s\S]*?</SOAP-ENV:Envelope>', response)[0]
                    else:
                        raise Exception('no soap response')
                    xml = ET.fromstring(response)
                    xmlstr = ET.tostring(xml, encoding='utf-8').decode('utf-8')

                    id = re.findall(r'<ns[0-9]:MessageId>[0-9a-fA-F]{8}\-[0-9a-fA-F]{4}\-[0-9a-fA-F]{4}\-[0-9a-fA-F]{4}\-[0-9a-fA-F]{12}</ns[0-9]:MessageId>', xmlstr)[0]
                    id = re.findall(r'[0-9a-fA-F]{8}\-[0-9a-fA-F]{4}\-[0-9a-fA-F]{4}\-[0-9a-fA-F]{4}\-[0-9a-fA-F]{12}', id)[0]

                    # read mtom
                    mtom_ids: list = []
                    mtom_ids_dict = mtom.get_mtom_attachments_ids(xmlstr)
                    if len(mtom_ids_dict.keys()) > 0:
                        mtom_files = mtom.get_mtom_files(raw_response, mtom_ids_dict)
                        for mtom_file in mtom_files.keys():
                            print(mtom_file)

                            multipart_form_data = {
                                'file': (mtom_file, mtom_files[mtom_file])
                            }
                            host = f'http://localhost:6504/api/v1/file/new'
                            response = requests.post(host, files=multipart_form_data, timeout=5)
                            if response.status_code == 200:
                                f_id = response.json()
                                f_meta = {
                                    "id": f_id['id'],
                                    "extension": f_id['path'].split(".")[-1]
                                }
                                mtom_ids.append(f_meta)
                                print(f"get mtom id: {f_id['id']}")

                    if not os.path.isdir('raw'):
                        os.mkdir('raw')
                    if not os.path.isdir(os.path.join('raw', str(smev_host_name))):
                        os.mkdir(os.path.join('raw', str(smev_host_name)))
                    if not os.path.isdir(os.path.join('raw', str(smev_host_name), 'worker')):
                        os.mkdir(os.path.join('raw', str(smev_host_name), 'worker'))
                    if not os.path.isdir(os.path.join('raw', str(smev_host_name), 'worker', queue)):
                        os.mkdir(os.path.join('raw', str(smev_host_name), 'worker', queue))
                    
                    with open(os.path.join('raw', str(smev_host_name), 'worker', queue, f'{id}-Response.xml'), 'wb') as f:
                        f.write(raw_response)

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
                        raise Exception(f'\tworker wrong smev responsse: {response}')
                    raise Exception(f'\tworker empty smev responsse')

                # update db record
                headers = {'content-type': 'application/json'}
                host = f'http://localhost:6502/api/v1/record/{id}/new'
                response = requests.get(host, headers=headers, timeout=5)
                if response.status_code != 200:
                    raise Exception(f'can not create record: status code {response.status_code}')

                body = {  "xml": xmlstr_req }
                headers = {'content-type': 'application/json'}
                host = f'http://localhost:6502/api/v1/record/{id}/GetRequestRequest'
                response = requests.put(host, json=body, headers=headers, timeout=5)
                if response.status_code != 200:
                    raise Exception(f'can not update GetRequestResponse mesage record: status code {response.status_code}')

                body = {  "xml": xmlstr, "mtoms": mtom_ids }
                headers = {'content-type': 'application/json'}
                host = f'http://localhost:6502/api/v1/record/{id}/GetRequestResponse'
                response = requests.put(host, json=body, headers=headers, timeout=5)
                if response.status_code != 200:
                    raise Exception(f'can not update GetRequestResponse mesage record: status code {response.status_code}')
                print(f'\tworker create new record {id}')
            except Exception as e:
                print(str(e), flush=True)
        