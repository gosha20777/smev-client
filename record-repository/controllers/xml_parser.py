import lxml.etree as ET
import io

def get_communication_type(xml_string, xpath="//*[local-name()='MessagePrimaryContent']/*"):
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
        root = sub_xml[0]
        return root.tag.split('{')[1].split('}')[0]
    else:
        raise Exception('xpath returns nothing')