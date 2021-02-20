from fastapi import APIRouter, HTTPException, Request, Response
from core.config import get_config
from pydantic import BaseModel
from datetime import datetime
from core.ros_reestr import archive_builder as rr_builder
import uuid
import base64
import requests
import re
import os

TEMP_DIR = 'tmp'

class SmevMesageRosReestrRequest(BaseModel):
    rosreestr_sert: str
    smev_sert: str
    smev_host: str
    request_type: int = 111300003000
    action_code: int = 659511111112
    cadastral_number: str
    name: str
    inn: str
    ogrn: str
    kpp: str
    reg_date: str
    declarant_kind: str
    object_type_code: str
    region_code: int
    verbose: bool =  False

class SmevIdResponse(BaseModel):
    id: str = "3745576a-06f4-11eb-9d06-10e7c6e703cb"

router = APIRouter()

@router.post('/send_request_ros_reestr', response_model=SmevIdResponse)
async def send_request(req: SmevMesageRosReestrRequest) -> SmevIdResponse:
    try:
        conf = {
            'requestType'    : req.request_type,
            'actionCode'     : req.action_code,
            'cadastralNumber': req.cadastral_number,
            'name'           : req.name,
            'inn'            : req.inn,
            'ogrn'           : req.ogrn,
            'kpp'            : req.kpp,
            'regDate'        : req.reg_date,
            'declarantKind'  : req.declarant_kind,
            'objectTypeCode' : req.object_type_code
        }
        
        base_dir = os.path.join(TEMP_DIR, f'{uuid.uuid1()}')
        os.mkdir(base_dir)
        sign_url = f"http://localhost:8080/v1/signer/pkcs7/{req.rosreestr_sert}"
        builder = rr_builder.EgrzBuilder(sign_url=sign_url, workdir=base_dir)
        zip_path = builder.build_zip(config=conf)
        print(zip_path)

        sign_url = f"http://localhost:8080/v1/signer/pkcs7/{req.rosreestr_sert}"
        b64_content = base64.b64encode(open(zip_path, 'rb').read())
        headers = {'content-type': 'application/text'}
        response = requests.post(sign_url, data=b64_content, headers=headers, timeout=5)
        assert response.status_code == 200, f'invalid pkcs7 signer response {response.text}'
        
        content_sig = response.content.decode()
        b64_content = b64_content.decode()

        # build smev message
        host = f"http://localhost:8080/v1/signer/message/{req.smev_sert}?type=1.1"
        body = { 
	        "id": "0",
	        "msgType": "SendRequestRequest",
	        "tagForSign": "SIGNED_BY_CONSUMER",
	        "xml": f"<req:Request xmlns:das=\"urn://x-artefacts-rosreestr-gov-ru/virtual-services/egrn-statement/dRegionsRF/1.0.0\" xmlns:req=\"urn://x-artefacts-rosreestr-gov-ru/virtual-services/egrn-statement/1.1.2\" xmlns:xsi=\"http://www.w3.org/2001/XMLSchema-instance\"><req:region>{req.region_code}</req:region><req:externalNumber>{uuid.uuid1()}</req:externalNumber><req:senderType>1</req:senderType><req:actionCode>{req.action_code}</req:actionCode><req:Attachment><req:IsMTOMAttachmentContent>true</req:IsMTOMAttachmentContent><req:RequestDescription><req:IsUnstructuredFormat>false</req:IsUnstructuredFormat><req:IsZippedPacket>true</req:IsZippedPacket><req:fileName>request.xml</req:fileName></req:RequestDescription><req:Statement><req:IsUnstructuredFormat>false</req:IsUnstructuredFormat><req:IsZippedPacket>true</req:IsZippedPacket><req:fileName>app_1.xml</req:fileName></req:Statement><req:File><req:IsUnstructuredFormat>true</req:IsUnstructuredFormat><req:IsZippedPacket>true</req:IsZippedPacket><req:fileName>app_1.xml.sig</req:fileName></req:File><req:File><req:IsUnstructuredFormat>true</req:IsUnstructuredFormat><req:IsZippedPacket>true</req:IsZippedPacket><req:fileName>request.xml.sig</req:fileName></req:File></req:Attachment></req:Request>",
	        "attachment": {
    	        "fileName": f"{uuid.uuid1()}.zip",
    	        "mimeType": "application/zip",
    	        "signature": content_sig,
    	        "content": b64_content
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
            raise Exception(f'Cant create record to db: api error {response.text}')

        host = f"http://localhost:8080/v1/record/{id}/SendRequestRequest"
        body = { "xml":  send_request_request }
        headers = {'content-type': 'application/json'}
        response = requests.put(host, json=body, headers=headers, timeout=5)
        if response.status_code != 200:
            raise Exception(f'Cant update record to db: SendRequestRequest {response.text}')
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
            raise Exception(f'Cant send to smev: api error {response.text}')
        
        response = response.json()
        send_request_response = response['xml']
        resp_id = response['id']
        if send_request_response == None:
            raise Exception(f'Cant send to smev: xml is empty {response.text}')
        if resp_id == None:
            raise Exception(f'Cant send to smev: id is empty {response.text}')
    except Exception as ex:
        raise HTTPException(400, str(ex))
    # update record db
    try:
        host = f"http://localhost:8080/v1/record/{id}/SendRequestResponse"
        body = { "xml":  send_request_response }
        headers = {'content-type': 'application/json'}
        response = requests.put(host, json=body, headers=headers, timeout=5)
        if response.status_code != 200:
            raise Exception(f'Cant update record to db: SendRequestResponse {response.text}')

        return SmevIdResponse(id=id)
    except Exception as ex:
        raise HTTPException(400, str(ex))