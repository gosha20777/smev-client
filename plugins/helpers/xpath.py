import io
import lxml.etree as ET
from lxml import objectify

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