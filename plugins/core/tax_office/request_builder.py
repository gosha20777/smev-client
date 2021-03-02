from typing import Optional

class TaxDictBuilder:
    def __init__(self, 
    org: str, 
    info: str,
    value: str,
    doc_id: str,
    doc_number: Optional[str]) -> None:
        self.org = org
        self.info = info
        self.value = value
        self.doc_id = doc_id
        self.doc_number = doc_number
    def build_request(self) -> dict:
        if self.org == 'OrganizationTypeEnum.ip':
            if self.info == 'InfoTypeEnum.inn':
                result = {
	                "ЗапросИП": {
		                "ИНН": self.value
	                },
	                "ИдДок": self.doc_id,
                    "НомерДела": self.doc_number
                }
            elif self.info == 'InfoTypeEnum.orgn':
                result = {
	                "ЗапросИП": {
		                "ОГРНИП": self.value
	                },
	                "ИдДок": self.doc_id,
                    "НомерДела": self.doc_number
                }
        elif self.org == 'OrganizationTypeEnum.ul':
            if self.info == 'InfoTypeEnum.inn':
                result = {
	                "ЗапросЮЛ": {
		                "ИННЮЛ": self.value
	                },
	                "ИдДок": self.doc_id,
                    "НомерДела": self.doc_number
                }
            elif self.info == 'InfoTypeEnum.orgn':
                result = {
	                "ЗапросЮЛ": {
		                "ОГРН": self.value
	                },
	                "ИдДок": self.doc_id,
                    "НомерДела": self.doc_number
                }
        return result