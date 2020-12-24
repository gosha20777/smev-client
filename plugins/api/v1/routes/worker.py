from fastapi import APIRouter, HTTPException, Request, Response
from core.config import get_config
from pydantic import BaseModel
from datetime import datetime
from helpers import xpath
from typing import List
import uuid
import requests
import re
import base64
import urllib

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
    
class FinishTaskRequest(BaseModel):
    id: str
    cert_type: str
    smev_host: str

class SmevIdResponse(BaseModel):
    id: str = "3745576a-06f4-11eb-9d06-10e7c6e703cb"

router = APIRouter()

@router.post('/reply', response_model=SmevIdResponse)
async def reply(req: SmevReply) -> SmevIdResponse:
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

        return SmevIdResponse(id=req.id)
    except Exception as ex:
        raise HTTPException(400, str(ex))

@router.post('/finish_response', response_model=SmevIdResponse)
async def finish_response(req: FinishTaskRequest):
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

        return SmevIdResponse(id=req.id)
    except Exception as ex:
        raise HTTPException(400, str(ex))