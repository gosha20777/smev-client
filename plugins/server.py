from fastapi import FastAPI, HTTPException, Request, Response
from pydantic import BaseModel
from datetime import datetime
import uuid
import requests
import re

class SmevMesageRequest(BaseModel):
    xsd_type: str
    json_template: dict
    cert_type: str
    smev_host: str

class Organization(BaseModel):
    name: str
    inn: str
    ogrn: str
    registration_date: str
    type_org: int

class Action(BaseModel):
    object_type_code: int
    cadastral_number: str

class Document(BaseModel):
    statement_type: int = 558630200000
    creation_date: str = str(datetime.now())
    request_type: str = 'extractRealty'
    processing_agreement: str = '01'
    data_agreement: str = '01'
    organization: Organization
    action: Action

class SmevMesageRosReestrRequest(BaseModel):
    message_sert: str
    attachment_sert: str
    smev_host: str
    region_code: int
    external_number: str = '832dc687-a2aa-4a3d-98fb-922e73e6a9e4'
    sender_type: str = 'Vedomstvo'
    action_code: int = 659511111112
    request_type: int = 111300003000
    document: Document

class FinishTaskRequest(BaseModel):
    id: str
    cert_type: str
    smev_host: str

app = FastAPI()

@app.post('/api/v1/plugin/send_request')
async def send_request(req: SmevMesageRequest):
    # json2xml
    try:
        host = f"http://localhost:8090/v1/json2xml/{req.xsd_type}"
        body = req.json_template
        headers = {'content-type': 'application/json'}
        response = requests.post(host, json=body, headers=headers, timeout=5)
        if response.status_code != 200:
            raise Exception('Cant convert json2xml: api error')
        
        response = response.json()
        send_request_request_teamplate = response['xml']
        if send_request_request_teamplate == None:
            raise Exception('Cant convert json2xml: xml is empty')
    except Exception as ex:
        raise HTTPException(400, str(ex))
    # sign mesage
    try:
        host = f"http://localhost:8090/v1/signer/message/{req.cert_type}"
        body = {
            "id": "0",
            "msgType": "SendRequestRequest",
            "tagForSign": "SIGNED_BY_CONSUMER",
            "xml":  send_request_request_teamplate
            }
        headers = {'content-type': 'application/json'}
        response = requests.post(host, json=body, headers=headers, timeout=5)
        if response.status_code != 200:
            raise Exception('Cant sign xml: api error')
        
        response = response.json()
        send_request_request = response['xml']
        id = response['id']
        if send_request_request == None:
            raise Exception('Cant sign xml: xml is empty')
        if id == None:
            raise Exception('Cant sign xml: id is empty')
    except Exception as ex:
        raise HTTPException(400, str(ex))
    # add record to db
    try:
        host = f"http://localhost:8090/v1/record/{id}/new"
        headers = {'content-type': 'application/json'}
        response = requests.get(host, headers=headers, timeout=5)
        if response.status_code != 200:
            raise Exception('Cant create record to db: api error')

        host = f"http://localhost:8090/v1/record/{id}/SendRequestRequest"
        body = { "xml":  send_request_request }
        headers = {'content-type': 'application/json'}
        response = requests.put(host, json=body, headers=headers, timeout=5)
        if response.status_code != 200:
            raise Exception('Cant update record to db: SendRequestRequest')
    except Exception as ex:
        raise HTTPException(400, str(ex))
    # send to smev
    try:
        host = f"http://localhost:8090/v1/send-to-smev/{req.smev_host}"
        body = {
            "id": id,
            "xml":  send_request_request
            }
        headers = {'content-type': 'application/json'}
        response = requests.post(host, json=body, headers=headers, timeout=10)
        if response.status_code != 200:
            raise Exception('Cant send to smev: api error')
        
        response = response.json()
        send_request_response = response['xml']
        resp_id = response['id']
        if send_request_response == None:
            raise Exception('Cant send to smev: xml is empty')
        if resp_id == None:
            raise Exception('Cant send to smev: id is empty')
    except Exception as ex:
        raise HTTPException(400, str(ex))
    # update record db
    try:
        host = f"http://localhost:8090/v1/record/{id}/SendRequestResponse"
        body = { "xml":  send_request_response }
        headers = {'content-type': 'application/json'}
        response = requests.put(host, json=body, headers=headers, timeout=5)
        if response.status_code != 200:
            raise Exception('Cant update record to db: SendRequestResponse')

        return { "id": id }
    except Exception as ex:
        raise HTTPException(400, str(ex))

@app.post('/api/v1/plugin/finish_request')
async def finish_task(req: FinishTaskRequest):
    # get record to db
    try:
        host = f"http://localhost:8090/v1/record/{req.id}/GetResponseResponse"
        headers = {'content-type': 'application/json'}
        response = requests.get(host, headers=headers, timeout=5)
        if response.status_code != 200:
            raise Exception('Cant get record to db: api error')
        if response == None:
            raise Exception('Cant get record to db: no such record')

        response = response.json()
        get_response_response = response['xml']
        finish_id = re.findall(r'<ns2:MessageId>[\s\S]*?</ns2:MessageId>', get_response_response)[0]
        finish_id = re.findall(r'[0-9a-fA-F]{8}\-[0-9a-fA-F]{4}\-[0-9a-fA-F]{4}\-[0-9a-fA-F]{4}\-[0-9a-fA-F]{12}', finish_id)[0]
    except Exception as ex:
        raise HTTPException(400, str(ex))
    # sign mesage
    try:
        host = f"http://localhost:8090/v1/signer/message/{req.cert_type}"
        body = { 
	            "id": finish_id,
	            "msgType": "AckRequest",
	            "tagForSign": "SIGNED_BY_CALLER"
        }
        headers = {'content-type': 'application/json'}
        response = requests.post(host, json=body, headers=headers, timeout=5)
        if response.status_code != 200:
            raise Exception('Cant sign xml: api error')
        
        response = response.json()
        ack_request = response['xml']
        if ack_request == None:
            raise Exception('Cant sign xml: xml is empty')
    except Exception as ex:
        raise HTTPException(400, str(ex))
    # send to smev
    try:
        host = f"http://localhost:8090/v1/send-to-smev/{req.smev_host}"
        body = {
            "id": finish_id,
            "xml":  ack_request
            }
        headers = {'content-type': 'application/json'}
        response = requests.post(host, json=body, headers=headers, timeout=10)
        if response.status_code != 200:
            raise Exception('Cant send to smev: api error')
    except Exception as ex:
        raise HTTPException(400, str(ex))
    # update record db
    try:
        host = f"http://localhost:8090/v1/record/{req.id}/AckRequest"
        body = { "xml":  ack_request }
        headers = {'content-type': 'application/json'}
        response = requests.put(host, json=body, headers=headers, timeout=5)
        if response.status_code != 200:
            raise Exception('Cant update record to db: AckRequest')

        return { "id": req.id }
    except Exception as ex:
        raise HTTPException(400, str(ex))

@app.post('/api/v1/plugin/send_request_ros_reestr')
async def send_request_rr(req: SmevMesageRosReestrRequest):
    try:
        # build smev message
        host = f"http://localhost:8090/v1/signer/message/{req.message_sert}?type=1.1"
        body = { 
	        "id": "0",
	        "msgType": "SendRequestRequest",
	        "tagForSign": "SIGNED_BY_CONSUMER",
	        "xml": "<req:Request xmlns:das=\"urn://x-artefacts-rosreestr-gov-ru/virtual-services/egrn-statement/dRegionsRF/1.0.0\" xmlns:req=\"urn://x-artefacts-rosreestr-gov-ru/virtual-services/egrn-statement/1.1.2\" xmlns:xsi=\"http://www.w3.org/2001/XMLSchema-instance\"><req:region>50</req:region><req:externalNumber>832dc687-a2aa-4a3d-98fb-922e73e6a9e4</req:externalNumber><req:senderType>Vedomstvo</req:senderType><req:actionCode>659511111112</req:actionCode><req:Attachment><req:IsMTOMAttachmentContent>true</req:IsMTOMAttachmentContent><req:RequestDescription><req:IsUnstructuredFormat>false</req:IsUnstructuredFormat><req:IsZippedPacket>true</req:IsZippedPacket><req:fileName>request.xml</req:fileName></req:RequestDescription><req:Statement><req:IsUnstructuredFormat>false</req:IsUnstructuredFormat><req:IsZippedPacket>true</req:IsZippedPacket><req:fileName>app_1.xml</req:fileName></req:Statement><req:File><req:IsUnstructuredFormat>true</req:IsUnstructuredFormat><req:IsZippedPacket>true</req:IsZippedPacket><req:fileName>app_1.xml.sig</req:fileName></req:File><req:File><req:IsUnstructuredFormat>true</req:IsUnstructuredFormat><req:IsZippedPacket>true</req:IsZippedPacket><req:fileName>request.xml.sig</req:fileName></req:File></req:Attachment></req:Request>",
	        "attachment": {
    	        "fileName": f"{str(uuid.uuid1())}.zip",
    	        "mimeType": "application/zip",
    	        "signature": "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",
    	        "content": "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"
	        }   
        }
        headers = {'content-type': 'application/json'}
        response = requests.post(host, json=body, headers=headers, timeout=5)
        if response.status_code != 200:
            raise Exception('Cant sign xml: api error')
        
        response = response.json()
        send_request_request = response['xml']
        id = response['id']
        if send_request_request == None:
            raise Exception('Cant sign xml: xml is empty')
        if id == None:
            raise Exception('Cant sign xml: id is empty')
    except Exception as ex:
        raise HTTPException(400, str(ex))
    # add record to db
    try:
        host = f"http://localhost:8090/v1/record/{id}/new"
        headers = {'content-type': 'application/json'}
        response = requests.get(host, headers=headers, timeout=5)
        if response.status_code != 200:
            raise Exception('Cant create record to db: api error')

        host = f"http://localhost:8090/v1/record/{id}/SendRequestRequest"
        body = { "xml":  send_request_request }
        headers = {'content-type': 'application/json'}
        response = requests.put(host, json=body, headers=headers, timeout=5)
        if response.status_code != 200:
            raise Exception('Cant update record to db: SendRequestRequest')
    except Exception as ex:
        raise HTTPException(400, str(ex))
    # send to smev
    try:
        host = f"http://localhost:8090/v1/send-to-smev/{req.smev_host}"
        body = {
            "id": id,
            "xml":  send_request_request
            }
        headers = {'content-type': 'application/json'}
        response = requests.post(host, json=body, headers=headers, timeout=10)
        if response.status_code != 200:
            raise Exception('Cant send to smev: api error')
        
        response = response.json()
        send_request_response = response['xml']
        resp_id = response['id']
        if send_request_response == None:
            raise Exception('Cant send to smev: xml is empty')
        if resp_id == None:
            raise Exception('Cant send to smev: id is empty')
    except Exception as ex:
        raise HTTPException(400, str(ex))
    # update record db
    try:
        host = f"http://localhost:8090/v1/record/{id}/SendRequestResponse"
        body = { "xml":  send_request_response }
        headers = {'content-type': 'application/json'}
        response = requests.put(host, json=body, headers=headers, timeout=5)
        if response.status_code != 200:
            raise Exception('Cant update record to db: SendRequestResponse')

        return { "id": id }
    except Exception as ex:
        raise HTTPException(400, str(ex))