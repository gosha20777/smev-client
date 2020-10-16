import os
from zeep import xsd
from lxml import etree
from .singleton import Singleton
from .transport import Transport

XSD_PATH = 'xsd'

class Loader(metaclass=Singleton):
    def __init__(self):
        self.schema = None

    def load(self, path: str):
        self.schema = None
        self.schema = xsd.Schema()
        for f in self.list_files(path):
            tree = etree.parse(f)
            t = Transport(path)
            schema = xsd.Schema(tree.getroot(), transport=t)
            self.schema.merge(schema)

    def list_files(self, path):
        return [os.path.join(path, d) for d in os.listdir(path) if os.path.isfile(os.path.join(path, d))]

    def get_element(self, name):
        template = '{{{}}}{}'
        for ns in self.schema.namespaces:
            fullname = template.format(ns, name)
            try:
                return self.schema.get_element(fullname)
            except:
                pass