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

BASE_URL = "http://mogt-ml:8080/v1/signer" # http://localhost:8090/v1/signer

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
        finish_id = re.findall(r'<ns[0-9]:MessageId>[0-9a-fA-F]{8}\-[0-9a-fA-F]{4}\-[0-9a-fA-F]{4}\-[0-9a-fA-F]{4}\-[0-9a-fA-F]{12}</ns[0-9]:MessageId>', get_response_response)[0]
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

@app.post('/api/v1/plugin/finish_response')
async def finish_task(req: FinishTaskRequest):
    # get record to db
    try:
        host = f"http://localhost:8090/v1/record/{req.id}/GetRequestResponse"
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
        host = f"http://localhost:8090/v1/signer/message/{req.cert_type}?type=1.1"
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

@app.post('/api/v1/plugin/reply')
async def reply_task(req: SmevReply):
    # 0 check ack request
    try:
        host = f"http://localhost:8090/v1/record/{req.id}/AckRequest"
        headers = {'content-type': 'application/json'}
        response = requests.get(host, headers=headers, timeout=5)
        if response.status_code != 200:
            raise Exception('Message chain has no AckRequest')
    except Exception as ex:
        raise HTTPException(400, str(ex))

    # 1 json2xml
    try:
        host = f"http://localhost:8090/v1/json2xml/{req.message.xsd_type}"
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
        host = f"http://localhost:8090/v1/record/{req.id}/GetRequestResponse"
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
            host = f"http://localhost:8090/v1/signer/pkcs7/{req.attachment.cert_type}"
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
        host = f"http://localhost:8090/v1/signer/message/{req.message.cert_type}?type=1.1"
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
        host = f"http://localhost:8090/v1/record/{req.id}/SendResponseRequest"
        body = { "xml":  send_response_request }
        headers = {'content-type': 'application/json'}
        response = requests.put(host, json=body, headers=headers, timeout=5)
        if response.status_code != 200:
            raise Exception('Cant update record to db: SendResponseRequest')
    except Exception as ex:
        raise HTTPException(400, str(ex))
    
    # 5 send to smev
    try:
        host = f"http://localhost:8090/v1/send-to-smev/{req.smev_host}"
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
        host = f"http://localhost:8090/v1/record/{req.id}/SendResponseResponse"
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
        host = f"http://localhost:8090/v1/signer/message/{req.message_sert}?type=1.1"
        body = { 
	        "id": "0",
	        "msgType": "SendRequestRequest",
	        "tagForSign": "SIGNED_BY_CONSUMER",
	        "xml": "<req:Request xmlns:das=\"urn://x-artefacts-rosreestr-gov-ru/virtual-services/egrn-statement/dRegionsRF/1.0.0\" xmlns:req=\"urn://x-artefacts-rosreestr-gov-ru/virtual-services/egrn-statement/1.1.2\" xmlns:xsi=\"http://www.w3.org/2001/XMLSchema-instance\"><req:region>50</req:region><req:externalNumber>832dc687-a2aa-4a3d-98fb-922e73e6a9e4</req:externalNumber><req:senderType>Vedomstvo</req:senderType><req:actionCode>659511111112</req:actionCode><req:Attachment><req:IsMTOMAttachmentContent>true</req:IsMTOMAttachmentContent><req:RequestDescription><req:IsUnstructuredFormat>false</req:IsUnstructuredFormat><req:IsZippedPacket>true</req:IsZippedPacket><req:fileName>request.xml</req:fileName></req:RequestDescription><req:Statement><req:IsUnstructuredFormat>false</req:IsUnstructuredFormat><req:IsZippedPacket>true</req:IsZippedPacket><req:fileName>app_1.xml</req:fileName></req:Statement><req:File><req:IsUnstructuredFormat>true</req:IsUnstructuredFormat><req:IsZippedPacket>true</req:IsZippedPacket><req:fileName>app_1.xml.sig</req:fileName></req:File><req:File><req:IsUnstructuredFormat>true</req:IsUnstructuredFormat><req:IsZippedPacket>true</req:IsZippedPacket><req:fileName>request.xml.sig</req:fileName></req:File></req:Attachment></req:Request>",
	        "attachment": {
    	        "fileName": "abf7c251-af10-11ea-ac86-556a22935496.zip",
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