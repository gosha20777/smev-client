import os
import argparse
import io
import lxml.etree as ET
from lxml import objectify
import json
import re
import requests

def parse_args(args):
    parser = argparse.ArgumentParser(description='pass worker test')
    parser.add_argument(
        '--smev-url',
        help='path to image',
        type=str,
        required=True
    )
    parser.add_argument(
        '--sign-url',
        help='path to image',
        type=str,
        required=True
    )
    parser.add_argument(
        '--config',
        help='path to h5 keras inference model',
        type=str,
        required=True
    )
    parser.add_argument(
        '--out',
        help='path to h5 keras inference model',
        type=str,
        required=True
    )
    return parser.parse_args(args)

def get_elenent_text(xml_string, xpath):
    if isinstance(xml_string, str):
        xml_string = xml_string.encode('utf-8')

    ns_map = dict([
        node for _, node in ET.iterparse(
            io.BytesIO(xml_string), events=['start-ns']
        )
    ])
    if '' in ns_map: del ns_map['']

    xml = ET.fromstring(xml_string)
    sub_xml = xml.xpath(xpath, namespaces=ns_map)

    if len(sub_xml) > 0:
        sub_xml = sub_xml[0]
        return sub_xml.text
    else:
        raise Exception('xpath returns nothing')

def get_message_id(message: str):
    try:
        id = re.findall(r'<ns[0-9]:MessageID>[0-9a-fA-F]{8}\-[0-9a-fA-F]{4}\-[0-9a-fA-F]{4}\-[0-9a-fA-F]{4}\-[0-9a-fA-F]{12}</ns[0-9]:MessageID>', message)[0]
        id = re.findall(r'[0-9a-fA-F]{8}\-[0-9a-fA-F]{4}\-[0-9a-fA-F]{4}\-[0-9a-fA-F]{4}\-[0-9a-fA-F]{12}', id)[0]
    except:
        id = ""
    return id

def get_reply(message: str):
    try:
        tag = re.findall(r'<ns[0-9]:ReplyTo>', message)[0]
        tag = tag.replace('<', '').replace('>', '')
        reply_to = re.findall(r'<ns[0-9]:ReplyTo>.*</ns[0-9]:ReplyTo>', message)[0]
        reply_to = reply_to.replace(f'<{tag}>', '')
        reply_to = reply_to.replace(f'</{tag}>', '')
    except:
        reply_to = ""
    return reply_to

def read_xml_teamplate(path: str):
    if not os.path.isfile(path):
        return ""
    text = open(path, 'r').read()
    if not '<?xml version="1.0" encoding="utf-8"?>' in text:
        return ""
    xml_teamplate = text.replace('<?xml version="1.0" encoding="utf-8"?>', '')
    return xml_teamplate

def get_message_from_queue(smev_url: str, sign_url: str):
    # build GetRequestRequest
    body = { 
        "id": "0", 
        "msgType": "GetRequestRequest", 
        "tagForSign": "SIGNED_BY_CALLER" 
        }
    headers = {'content-type': 'application/json'}
    response = requests.post(sign_url, json=body, headers=headers, timeout=5)
    if response.status_code != 200:
        raise Exception('can not build GetRequestRequest mesage')
    body = response.json()
    GetRequestRequest = body['xml']
    
    # send request to smev   
    headers = {'content-type': 'application/json;  charset=utf-8'}
    response = requests.post(smev_url, json=body, headers=headers, timeout=10)
    if response.status_code != 200:
        raise Exception('can not get GetRequestResponse from smev')
    body = response.json()
    GetRequestResponse = body['xml']
    return GetRequestRequest, GetRequestResponse
    
def ack_message(smev_url: str, sign_url: str, message_id: str):
    # build AckRequest
    body = { 
        "id": message_id, 
        "msgType": "AckRequest", 
        "tagForSign": "SIGNED_BY_CALLER" 
        }
    headers = {'content-type': 'application/json'}
    response = requests.post(sign_url, json=body, headers=headers, timeout=5)
    if response.status_code != 200:
        raise Exception('can not build AckRequest mesage')
    body = response.json()
    AckRequest = body['xml']
    
    # send request to smev   
    headers = {'content-type': 'application/json;  charset=utf-8'}
    response = requests.post(smev_url, json=body, headers=headers, timeout=10)
    if response.status_code != 200:
        raise Exception('can not get AckResponse from smev')
    body = response.json()
    AckResponse = body['xml']
    return AckRequest, AckResponse

def send_response_to_smev(smev_url: str, sign_url: str, reply_to: str, xml_teamplate: str):
    # build SendResponseRequest
    body = { 
        "id": "0",
        "msgType": "SendResponseRequest",
        "tagForSign": "SIGNED_BY_CONSUMER",
        "to": reply_to,
        "xml": xml_teamplate
        }
    headers = {'content-type': 'application/json; charset=utf-8'}
    response = requests.post(sign_url, json=body, headers=headers, timeout=5)
    if response.status_code != 200:
        raise Exception('can not build SendResponseRequest mesage')
    body = response.json()
    SendResponseRequest = body['xml']
    
    # send request to smev   
    headers = {'content-type': 'application/json;  charset=utf-8'}
    response = requests.post(smev_url, json=body, headers=headers, timeout=10)
    if response.status_code != 200:
        raise Exception('can not get SendResponseResponse from smev')
    body = response.json()
    SendResponseResponse = body['xml']
    return SendResponseRequest, SendResponseResponse
    
def pass_tests(smev_url: str,  sign_url: str, config: dict, save_path: str):
    tests_count = len(list(config.keys()))
    passed_count = 0
    while passed_count < tests_count:
        try:
            GetRequestRequest, GetRequestResponse = get_message_from_queue(smev_url=smev_url, sign_url=sign_url)
            id = get_message_id(GetRequestResponse)
            if id == "":
                print("GetRequestResponse id is null")
                continue
            reply_to = get_reply(GetRequestResponse)
            if reply_to == "":
                print("GetRequestResponse reply_to is null")
                continue
            if id not in list(config.keys()):
                print(f"get `{id}` but it not in tests")
                continue
            xml_teamplate = read_xml_teamplate(config[id])
            if reply_to == "":
                print(f"xml_teamplate from test {id} is null")
                continue

            AckRequest, AckResponse = ack_message(smev_url=smev_url, sign_url=sign_url, message_id=id)
            SendResponseRequest, SendResponseResponse = send_response_to_smev(smev_url=smev_url, sign_url=sign_url, reply_to=reply_to, xml_teamplate=xml_teamplate)
            
            if not os.path.exists(os.path.join(save_path, id)):
                os.mkdir(os.path.join(save_path, id))
            
            open(os.path.join(save_path, id, 'GetRequestRequest.xml'), 'w').write(GetRequestRequest)
            open(os.path.join(save_path, id, 'GetRequestResponse.xml'), 'w').write(GetRequestResponse)
            open(os.path.join(save_path, id, 'AckRequest.xml'), 'w').write(AckRequest)
            open(os.path.join(save_path, id, 'AckResponse.xml'), 'w').write(AckResponse)
            open(os.path.join(save_path, id, 'SendResponseRequest.xml'), 'w').write(SendResponseRequest)
            open(os.path.join(save_path, id, 'SendResponseResponse.xml'), 'w').write(SendResponseResponse)
            
            passed_count = passed_count + 1
            print(f'test {id} passed: {passed_count} of {tests_count}')
        except Exception as ex:
            print(f'error {ex}')

def main(args=None):
    args = parse_args(args)
    if not os.path.exists(args.out):
        os.mkdir(args.out)

    config = json.load(open(args.config, 'r'))

    pass_tests(smev_url=args.smev_url, sign_url=args.sign_url, config=config, save_path=args.out)
    print('passed!')

if __name__ == '__main__':
    main()

    






 
