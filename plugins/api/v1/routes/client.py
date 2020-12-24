from fastapi import APIRouter, HTTPException, Request, Response
from core.config import get_config
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

class FinishTaskRequest(BaseModel):
    id: str
    cert_type: str
    smev_host: str

class SmevIdResponse(BaseModel):
    id: str = "3745576a-06f4-11eb-9d06-10e7c6e703cb"

router = APIRouter()

@router.post('/send_request', response_model=SmevIdResponse)
async def send_request(req: SmevMesageRequest) -> SmevIdResponse:
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
    
        return SmevIdResponse(id=id)
    except Exception as ex:
        raise HTTPException(400, str(ex))

@router.post('/finish_request', response_model=SmevIdResponse)
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

        return SmevIdResponse(id=req.id)
    except Exception as ex:
        raise HTTPException(400, str(ex))