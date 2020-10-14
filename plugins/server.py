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

class SmevReplyAttachment(BaseModel):
    files: List[str]
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
    has_attachment = False
    if req.attachment != None and len(req.attachment.files) > 0:
        has_attachment = True
        try:
            with urllib.request.urlopen(req.attachment.files[0]) as f:
                content = f.read()
        except:
            raise Exception('Cant download attachment: api error')
        b64_content = base64.b64encode(content)
        host = f"http://localhost:8090/v1/signer/pkcs7/{req.attachment.cert_type}"
        headers = {'content-type': 'application/text; charset=utf-8'}
        response = requests.post(host, data=b64_content, headers=headers, timeout=5)
        if response.status_code != 200:
            raise Exception('Cant sign attachment: api error')
        signature_str = response.content.decode()
        b64_content = b64_content.decode()
        hash_object = hashlib.sha1(content)
        filename = hash_object.hexdigest()
        

    # 3 sign mesage
    try:
        host = f"http://localhost:8090/v1/signer/message/{req.message.cert_type}?type=1.1"
        if has_attachment == True:
            body = {
                "id": "0",
                "msgType": "SendResponseRequest",
                "tagForSign": "SIGNED_BY_CONSUMER",
                "xml":  send_response_request_teamplate,
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
    	        "fileName": "abf7c251-af10-11ea-ac86-556a22935495.zip",
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