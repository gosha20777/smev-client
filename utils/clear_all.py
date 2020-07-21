import requests
import json
import re
import argparse
import os


def finish_task(filename: str, base_url: str, cert_type: str, smev_host: str):
    # get record to db
    try:
        get_response_response = open(filename, 'r').read()
        finish_id = re.findall(r'<ns[0-9]:MessageId>[0-9a-fA-F]{8}\-[0-9a-fA-F]{4}\-[0-9a-fA-F]{4}\-[0-9a-fA-F]{4}\-[0-9a-fA-F]{12}</ns[0-9]:MessageId>', get_response_response)[0]
        finish_id = re.findall(r'[0-9a-fA-F]{8}\-[0-9a-fA-F]{4}\-[0-9a-fA-F]{4}\-[0-9a-fA-F]{4}\-[0-9a-fA-F]{12}', finish_id)[0]
    except Exception as ex:
        raise Exception(str(ex))
    # sign mesage
    try:
        host = f"http://{base_url}/v1/signer/message/{cert_type}?type=1.2"
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
        raise Exception(str(ex))
    # send to smev
    try:
        host = f"http://{base_url}/v1/send-to-smev/{smev_host}"
        body = {
            "id": finish_id,
            "xml":  ack_request
            }
        headers = {'content-type': 'application/json'}
        response = requests.post(host, json=body, headers=headers, timeout=10)
        if response.status_code != 200:
            raise Exception('Cant send to smev: api error')
        print(f'AckResponse: {response.content.decode("utf-8", errors="ignore")}')
    except Exception as ex:
        raise Exception(str(ex))

def parse_args(args):
    """ Parse the arguments.
    """
    parser = argparse.ArgumentParser(description='Evaluation script for a RetinaNet network.')
    parser.add_argument('--dir', help='Path to RetinaNet model.')
    parser.add_argument('--url', help='Visile gpu device. Set to -1 if CPU')
    parser.add_argument('--cert', help='Path to RetinaNet model.')
    parser.add_argument('--smev', help='Visile gpu device. Set to -1 if CPU')
    return parser.parse_args(args)

def main(args=None):
    args = parse_args(args)
    if not os.path.isdir(args.dir):
        raise Exception('invalid dir')
    files = os.listdir(args.dir)
    for f in files:
        fname = os.path.join(args.dir, f)
        if not os.path.isfile(fname):
            continue
        print(fname)
        finish_task(filename=fname, base_url=args.url, cert_type=args.cert, smev_host=args.smev)

if __name__ == '__main__':
    main()
