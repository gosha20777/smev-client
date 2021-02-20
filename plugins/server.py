from fastapi import FastAPI, HTTPException, Request, Response
from pydantic import BaseModel
from typing import List
from datetime import datetime
from helpers import xpath
import uuid
import requests
import re
import base64
import urllib
import hashlib

BASE_URL = "http://localhost:8080/v1/signer"

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

class SmevReplyMessage(BaseModel):
    xsd_type: str
    json_template: dict
    cert_type: str

class SmevReplyFile(BaseModel):
    url: str
    name: str

class SmevReplyAttachment(BaseModel):
    files: List[SmevReplyFile]
    cert_type: str

class SmevReply(BaseModel):
    smev_host: str
    id: str
    message: SmevReplyMessage
    attachment: SmevReplyAttachment = None

app = FastAPI()

@app.post('/api/v1/plugin/send_request')
async def send_request(req: SmevMesageRequest):
    # json2xml
    try:
        host = f"http://localhost:8080/v1/json2xml/{req.xsd_type}"
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
        host = f"http://localhost:8080/v1/signer/message/{req.cert_type}"
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
        host = f"http://localhost:8080/v1/record/{id}/new"
        headers = {'content-type': 'application/json'}
        response = requests.get(host, headers=headers, timeout=5)
        if response.status_code != 200:
            raise Exception('Cant create record to db: api error')

        host = f"http://localhost:8080/v1/record/{id}/SendRequestRequest"
        body = { "xml":  send_request_request }
        headers = {'content-type': 'application/json'}
        response = requests.put(host, json=body, headers=headers, timeout=5)
        if response.status_code != 200:
            raise Exception('Cant update record to db: SendRequestRequest')
    except Exception as ex:
        raise HTTPException(400, str(ex))
    # send to smev
    try:
        host = f"http://localhost:8080/v1/send-to-smev/{req.smev_host}"
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
        host = f"http://localhost:8080/v1/record/{id}/SendRequestResponse"
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
        host = f"http://localhost:8080/v1/record/{req.id}/GetResponseResponse"
        headers = {'content-type': 'application/json'}
        response = requests.get(host, headers=headers, timeout=5)
        if response.status_code != 200:
            raise Exception('Cant get record to db: api error')
        if response == None:
            raise Exception('Cant get record to db: no such record')

        response = response.json()
        get_response_response = response['xml']
        finish_id = re.findall(r'<ns[0-9]:MessageId>[0-9a-fA-F]{8}\-[0-9a-fA-F]{4}\-[0-9a-fA-F]{4}\-[0-9a-fA-F]{4}\-[0-9a-fA-F]{12}</ns[0-9]:MessageId>', get_response_response)[0]
        finish_id = re.findall(r'[0-9a-fA-F]{8}\-[0-9a-fA-F]{4}\-[0-9a-fA-F]{4}\-[0-9a-fA-F]{4}\-[0-9a-fA-F]{12}', finish_id)[0]
    except Exception as ex:
        raise HTTPException(400, str(ex))
    # sign mesage
    try:
        host = f"http://localhost:8080/v1/signer/message/{req.cert_type}"
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
        host = f"http://localhost:8080/v1/send-to-smev/{req.smev_host}"
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
        host = f"http://localhost:8080/v1/record/{req.id}/AckRequest"
        body = { "xml":  ack_request }
        headers = {'content-type': 'application/json'}
        response = requests.put(host, json=body, headers=headers, timeout=5)
        if response.status_code != 200:
            raise Exception('Cant update record to db: AckRequest')

        return { "id": req.id }
    except Exception as ex:
        raise HTTPException(400, str(ex))

@app.post('/api/v1/plugin/finish_response')
async def finish_task(req: FinishTaskRequest):
    # get record to db
    try:
        host = f"http://localhost:8080/v1/record/{req.id}/GetRequestResponse"
        headers = {'content-type': 'application/json'}
        response = requests.get(host, headers=headers, timeout=5)
        if response.status_code != 200:
            raise Exception('Cant get record to db: api error')
        if response == None:
            raise Exception('Cant get record to db: no such record')

        response = response.json()
        get_response_response = response['xml']
        finish_id = req.id
    except Exception as ex:
        raise HTTPException(400, str(ex))
    # sign mesage
    try:
        host = f"http://localhost:8080/v1/signer/message/{req.cert_type}?type=1.1"
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
        host = f"http://localhost:8080/v1/send-to-smev/{req.smev_host}"
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
        host = f"http://localhost:8080/v1/record/{req.id}/AckRequest"
        body = { "xml":  ack_request }
        headers = {'content-type': 'application/json'}
        response = requests.put(host, json=body, headers=headers, timeout=5)
        if response.status_code != 200:
            raise Exception('Cant update record to db: AckRequest')

        return { "id": req.id }
    except Exception as ex:
        raise HTTPException(400, str(ex))

@app.post('/api/v1/plugin/reply')
async def reply_task(req: SmevReply):
    # 0 check ack request
    try:
        host = f"http://localhost:8080/v1/record/{req.id}/AckRequest"
        headers = {'content-type': 'application/json'}
        response = requests.get(host, headers=headers, timeout=5)
        if response.status_code != 200:
            raise Exception('Message chain has no AckRequest')
    except Exception as ex:
        raise HTTPException(400, str(ex))

    # 1 json2xml
    try:
        host = f"http://localhost:8080/v1/json2xml/{req.message.xsd_type}"
        body = req.message.json_template
        headers = {'content-type': 'application/json'}
        response = requests.post(host, json=body, headers=headers, timeout=5)
        if response.status_code != 200:
            raise Exception('Cant convert json2xml: api error')

        response = response.json()
        send_response_request_teamplate = response['xml']
        if send_response_request_teamplate == None:
            raise Exception('Cant convert json2xml: xml is empty')
    except Exception as ex:
        raise HTTPException(400, str(ex))

    # 2 get Reply To param
    try:
        host = f"http://localhost:8080/v1/record/{req.id}/GetRequestResponse"
        headers = {'content-type': 'application/json'}
        response = requests.get(host, headers=headers, timeout=5)
        if response.status_code != 200:
            raise Exception('Cant convert get Get Request Response: api error')
        
        response = response.json()
        get_request_response_xml = response['xml']
        reply_to = xpath.get_elenent_text(get_request_response_xml, "//*[local-name()='ReplyTo']")
    except Exception as ex:
        raise HTTPException(400, str(ex))

    # 3 sign attachment
    try:
        has_attachment = False
        if req.attachment != None and len(req.attachment.files) > 0:
            has_attachment = True
            try:
                filename = req.attachment.files[0].name
                with urllib.request.urlopen(req.attachment.files[0].url) as f:
                    content = f.read()
            except Exception as ex:
                raise Exception(f'Cant download attachment: api error {ex}')
            b64_content = base64.b64encode(content)
            host = f"http://localhost:8080/v1/signer/pkcs7/{req.attachment.cert_type}"
            headers = {'content-type': 'application/text; charset=utf-8'}
            response = requests.post(host, data=b64_content, headers=headers, timeout=5)
            if response.status_code != 200:
                raise Exception('Cant sign attachment: api error')
            signature_str = response.content.decode()
            b64_content = b64_content.decode()
    except Exception as ex:
        raise HTTPException(400, str(ex))        

    # 3 sign mesage
    try:
        host = f"http://localhost:8080/v1/signer/message/{req.message.cert_type}?type=1.1"
        if has_attachment == True:
            body = {
                "id": "0",
                "msgType": "SendResponseRequest",
                "tagForSign": "SIGNED_BY_CONSUMER",
                "xml":  send_response_request_teamplate,
                "to": reply_to,
                "attachment": {
    	            "fileName": filename,
    	            "mimeType": "application/binary",
    	            "signature": signature_str,
    	            "content": b64_content
	                }
                }
        else:
            body = {
                "id": "0",
                "msgType": "SendResponseRequest",
                "tagForSign": "SIGNED_BY_CONSUMER",
                "to": reply_to,
                "xml":  send_response_request_teamplate
                }
        headers = {'content-type': 'application/json'}
        response = requests.post(host, json=body, headers=headers, timeout=5)
        if response.status_code != 200:
            raise Exception('Cant sign xml: api error')
        
        response = response.json()
        send_response_request = response['xml']
        id = response['id']
        if send_response_request == None:
            raise Exception('Cant sign xml: xml is empty')
        if id == None:
            raise Exception('Cant sign xml: id is empty')
    except Exception as ex:
        raise HTTPException(400, str(ex))

    # 4 add record to db
    try:
        host = f"http://localhost:8080/v1/record/{req.id}/SendResponseRequest"
        body = { "xml":  send_response_request }
        headers = {'content-type': 'application/json'}
        response = requests.put(host, json=body, headers=headers, timeout=5)
        if response.status_code != 200:
            raise Exception('Cant update record to db: SendResponseRequest')
    except Exception as ex:
        raise HTTPException(400, str(ex))
    
    # 5 send to smev
    try:
        host = f"http://localhost:8080/v1/send-to-smev/{req.smev_host}"
        body = {
            "id": id,
            "xml":  send_response_request
            }
        headers = {'content-type': 'application/json'}
        response = requests.post(host, json=body, headers=headers, timeout=10)
        if response.status_code != 200:
            raise Exception('Cant send to smev: api error')
        
        response = response.json()
        send_response_response = response['xml']
        resp_id = response['id']
        if send_response_response == None:
            raise Exception('Cant send to smev: xml is empty')
        if resp_id == None:
            raise Exception('Cant send to smev: id is empty')
    except Exception as ex:
        raise HTTPException(400, str(ex))

    # 6 update record db
    try:
        host = f"http://localhost:8080/v1/record/{req.id}/SendResponseResponse"
        body = { "xml":  send_response_response }
        headers = {'content-type': 'application/json'}
        response = requests.put(host, json=body, headers=headers, timeout=5)
        if response.status_code != 200:
            raise Exception('Cant update record to db: SendResponseResponse')

        return { "id": req.id }
    except Exception as ex:
        raise HTTPException(400, str(ex))

@app.post('/api/v1/plugin/send_request_ros_reestr')
async def send_request_rr(req: SmevMesageRosReestrRequest):
    try:
        # build smev message
        host = f"http://localhost:8080/v1/signer/message/{req.message_sert}?type=1.1"
        body = { 
	        "id": "0",
	        "msgType": "SendRequestRequest",
	        "tagForSign": "SIGNED_BY_CONSUMER",
	        "xml": "<req:Request xmlns:das=\"urn://x-artefacts-rosreestr-gov-ru/virtual-services/egrn-statement/dRegionsRF/1.0.0\" xmlns:req=\"urn://x-artefacts-rosreestr-gov-ru/virtual-services/egrn-statement/1.1.2\" xmlns:xsi=\"http://www.w3.org/2001/XMLSchema-instance\"><req:region>50</req:region><req:externalNumber>832dc687-a2aa-4a3d-98fb-922e73e6a9e4</req:externalNumber><req:senderType>1</req:senderType><req:actionCode>659511111112</req:actionCode><req:Attachment><req:IsMTOMAttachmentContent>true</req:IsMTOMAttachmentContent><req:RequestDescription><req:IsUnstructuredFormat>false</req:IsUnstructuredFormat><req:IsZippedPacket>true</req:IsZippedPacket><req:fileName>request.xml</req:fileName></req:RequestDescription><req:Statement><req:IsUnstructuredFormat>false</req:IsUnstructuredFormat><req:IsZippedPacket>true</req:IsZippedPacket><req:fileName>app_1.xml</req:fileName></req:Statement><req:File><req:IsUnstructuredFormat>true</req:IsUnstructuredFormat><req:IsZippedPacket>true</req:IsZippedPacket><req:fileName>app_1.xml.sig</req:fileName></req:File><req:File><req:IsUnstructuredFormat>true</req:IsUnstructuredFormat><req:IsZippedPacket>true</req:IsZippedPacket><req:fileName>request.xml.sig</req:fileName></req:File></req:Attachment></req:Request>",
	        "attachment": {
    	        "fileName": "abf7c251-af10-11ea-ac86-556a22935497.zip",
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
        host = f"http://localhost:8080/v1/record/{id}/new"
        headers = {'content-type': 'application/json'}
        response = requests.get(host, headers=headers, timeout=5)
        if response.status_code != 200:
            raise Exception('Cant create record to db: api error')

        host = f"http://localhost:8080/v1/record/{id}/SendRequestRequest"
        body = { "xml":  send_request_request }
        headers = {'content-type': 'application/json'}
        response = requests.put(host, json=body, headers=headers, timeout=5)
        if response.status_code != 200:
            raise Exception('Cant update record to db: SendRequestRequest')
    except Exception as ex:
        raise HTTPException(400, str(ex))
    # send to smev
    try:
        host = f"http://localhost:8080/v1/send-to-smev/{req.smev_host}"
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
        host = f"http://localhost:8080/v1/record/{id}/SendRequestResponse"
        body = { "xml":  send_request_response }
        headers = {'content-type': 'application/json'}
        response = requests.put(host, json=body, headers=headers, timeout=5)
        if response.status_code != 200:
            raise Exception('Cant update record to db: SendRequestResponse')

        return { "id": id }
    except Exception as ex:
        raise HTTPException(400, str(ex))