from pydantic import BaseModel
from fastapi import APIRouter, HTTPException, Request, Response
from fastapi_utils.enums import StrEnum
from enum import auto
from typing import Optional
from core.tax_office.request_builder import TaxDictBuilder
import requests

class OrganizationTypeEnum(StrEnum):
    ul = auto()
    ip = auto()

class InfoTypeEnum(StrEnum):
    orgn = auto()
    inn = auto()

class SmevMesageTaxrRequest(BaseModel):
    smev_sert: str
    smev_host: str
    organization: OrganizationTypeEnum
    information: InfoTypeEnum
    doc_id: str
    doc_number: Optional[str]
    value: str
    
class SmevIdResponse(BaseModel):
    id: str = "3745576a-06f4-11eb-9d06-10e7c6e703cb"

router = APIRouter()

@router.post('/tax_inn_ul', response_model=SmevIdResponse)
async def send_request(req: SmevMesageTaxrRequest) -> SmevIdResponse:
    builder = TaxDictBuilder(
        org=str(req.organization), 
        info=str(req.information),
        value=req.value,
        doc_id=req.doc_id,
        doc_number=req.doc_number
    )
    
    try:
        # build smev message
        if req.organization == OrganizationTypeEnum.ul:
            xsd_type = "16351/FNSVipULRequest"
        elif req.organization == OrganizationTypeEnum.ip:
            xsd_type = "15980/FNSVipIPRequest"
        host = f"http://localhost:8080/v1/json2xml/{xsd_type}"
        body = builder.build_request()
        headers = {'content-type': 'application/json'}
        response = requests.post(host, json=body, headers=headers, timeout=5)
        if response.status_code != 200:
            raise Exception('Cant convert json2xml: api error')
        
        response = response.json()
        send_request_request_teamplate = response['xml']
        if send_request_request_teamplate == None:
            raise Exception('Cant convert json2xml: xml is empty')

        # sign smev message
        host = f"http://localhost:8080/v1/signer/message/{req.smev_sert}?type=1.1"
        body = { 
	        "id": "0",
	        "msgType": "SendRequestRequest",
	        "tagForSign": "SIGNED_BY_CONSUMER",
	        "xml": send_request_request_teamplate,   
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

        # add record to db
        host = f"http://localhost:8080/v1/record/{id}/new"
        headers = {'content-type': 'application/json'}
        response = requests.get(host, headers=headers, timeout=5)
        if response.status_code != 200:
            raise Exception(f'Cant create record to db: api error {response.text}')
        host = f"http://localhost:8080/v1/record/{id}/SendRequestRequest"
        body = { "xml":  send_request_request }
        headers = {'content-type': 'application/json'}
        response = requests.put(host, json=body, headers=headers, timeout=5)
        if response.status_code != 200:
            raise Exception(f'Cant update record to db: SendRequestRequest {response.text}')

        # send message to smev
        host = f"http://localhost:8080/v1/send-to-smev/{req.smev_host}"
        body = {
            "id": id,
            "xml":  send_request_request
            }
        headers = {'content-type': 'application/json'}
        response = requests.post(host, json=body, headers=headers, timeout=10)
        if response.status_code != 200:
            raise Exception(f'Cant send to smev: api error {response.text}')
        response = response.json()
        send_request_response = response['xml']
        resp_id = response['id']
        if send_request_response == None:
            raise Exception(f'Cant send to smev: xml is empty {response.text}')
        if resp_id == None:
            raise Exception(f'Cant send to smev: id is empty {response.text}')

        # update record db
        host = f"http://localhost:8080/v1/record/{id}/SendRequestResponse"
        body = { "xml":  send_request_response }
        headers = {'content-type': 'application/json'}
        response = requests.put(host, json=body, headers=headers, timeout=5)
        if response.status_code != 200:
            raise Exception(f'Cant update record to db: SendRequestResponse {response.text}')

        return SmevIdResponse(id=id)
    except Exception as ex:
        raise HTTPException(400, detail=str(ex))