import io
import lxml.etree as ET
from lxml import objectify

def get_xml_string(xml_string, xpath):
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
        # cleanup namespaces
        # convert to string and back to make cleanup_namespaces() work
        xml_string = ET.tostring(sub_xml, method='xml', encoding='utf-8').decode('utf-8') 
        claen_xml_string = xml_string.encode('utf-8')
        root = ET.fromstring(claen_xml_string)
        ET.cleanup_namespaces(root)
        claen_xml_string = ET.tostring(root, method='xml', encoding='utf-8').decode('utf-8')
        return claen_xml_string
    else:
        raise Exception('xpath returns nothing')