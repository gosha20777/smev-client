import re
import lxml.etree as ET
import io

def get_mtom_attachments_ids(xml_string, xpath="//*[local-name()='AttachmentContentList']/*"):
    if isinstance(xml_string, str):
        xml_string = xml_string.encode('utf-8')

    ns_map = dict([
        node for _, node in ET.iterparse(
            io.BytesIO(xml_string), events=['start-ns']
        )
    ])
    if '' in ns_map: del ns_map['']

    xml = ET.fromstring(xml_string)
    attachment_content_list = xml.xpath(xpath, namespaces=ns_map)
    attachment_dict: dict = {} 
    for attachment_content in attachment_content_list:
        xml_string = ET.tostring(attachment_content, method='xml', encoding='utf-8').decode('utf-8')
        ext = re.findall(r'<Id>.*</Id>', xml_string)[0].replace('<Id>', '').replace('</Id>', '').split('.')[-1]
        id = re.findall(r'[0-9a-fA-F]{8}\-[0-9a-fA-F]{4}\-[0-9a-fA-F]{4}\-[0-9a-fA-F]{4}\-[0-9a-fA-F]{12}\-[0-9a-fA-F]{6}', xml_string)[0]
        attachment_dict.update({id: ext})
    return attachment_dict

def get_mtom_files(data: bytes, attachment_dict: dict):
    data_lines = data.split(b'\n')

    parts: dict = {}
    content = None
    i = 0

    while i < len(data_lines) - 1:
        data_lines[i] = data_lines[i] + b'\n'
        if data_lines[i].decode('utf-8', errors='ignore').startswith('--uuid:'):
            metadata = [
                data_lines[i+1].decode('utf-8', errors='ignore'),
                data_lines[i+2].decode('utf-8', errors='ignore'),
                data_lines[i+3].decode('utf-8', errors='ignore')
            ]

            for md in metadata:
                if md.startswith('Content-ID:'):
                    content_id = md.replace('Content-ID: ','')
                    if 'root.message' in content_id:
                        content = 'message'
                        parts.update({content: ''})
                    else:
                        try:
                            content = re.findall(r'[0-9a-fA-F]{8}\-[0-9a-fA-F]{4}\-[0-9a-fA-F]{4}\-[0-9a-fA-F]{4}\-[0-9a-fA-F]{12}\-[0-9a-fA-F]{6}', md)[0]
                            parts.update({content: b''})
                        except:
                            content = None
                            continue
            i = i + 4
        else:
            if content != None:
                if content == 'message':
                    line = data_lines[i].decode('utf-8', errors='ignore')
                else:
                    line = data_lines[i]
                parts[content] = parts[content] + line
        i = i + 1
    
    result: dict = {}

    for key in parts.keys():
        if key in attachment_dict.keys():
            result.update({f'{key}.{attachment_dict[key]}': parts[key]})
    return result