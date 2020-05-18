from .singleton import Singleton
from .xsd_loader import Loader
from lxml import etree

class XsdProcessor(metaclass=Singleton):
    def __init__(self):
        self.loader = Loader()

    async def process(self, element_type, params):
        xsd_element = self.loader.get_element(element_type)
        
        if not xsd_element:
            raise Exception('No such element_type {}.'.format(element_type))
        val = xsd_element(**params) if isinstance(params, dict) else xsd_element(*params)

        root = etree.Element("content_root")
        xsd_element.render(root, val)
        return etree.tostring(root, encoding='utf-8').decode().replace('<content_root>', '', 1).replace('</content_root>', '', 1)