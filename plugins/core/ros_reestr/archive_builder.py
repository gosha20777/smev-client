import uuid
from datetime import datetime
from zipfile import ZipFile
import os
import base64
import requests

class BaseBuilder:
    def __init__(self, sign_url: str, workdir: str) -> None:
        self._sign_url = sign_url
        assert os.path.isdir(workdir), f'no such dir {workdir}'
        self._workdir = workdir
    def build_zip(self, config: dict) -> str:
        pass

class EgrzBuilder(BaseBuilder):
    def build_zip(self, config: dict) -> str:
        assert 'requestType' in config.keys(), 'no requestType in config'
        assert 'cadastralNumber' in config.keys(), 'no cadastralNumber in config'
        assert 'name' in config.keys(), 'no name in config'
        assert 'inn' in config.keys(), 'no inn in config'
        assert 'ogrn' in config.keys(), 'no ogrn in config'
        assert 'kpp' in config.keys(), 'no kpp in config'
        assert 'regDate' in config.keys(), 'no regDate in config'
        assert 'declarantKind' in config.keys(), 'no declarantKind in config'
        assert 'objectTypeCode' in config.keys(), 'no objectTypeCode in config'

        # request.xml
        request_xml = '<?xml version="1.0" encoding="UTF-8"?>' + \
        '<request xmlns="http://rosreestr.ru/services/v0.12/TRequest">' + \
        '<statementFile>' + \
        '<fileName>app_1.xml</fileName>' + \
        '</statementFile>' + \
        '<file>' + \
        '<fileName>request.xml</fileName>' + \
        '</file>' + \
        f'<requestType>{config["requestType"]}</requestType>' + \
        '</request>'

        # app_1.xml
        app_1_xml = '<?xml version="1.0" encoding="UTF-8"?>' + \
        f'<tns:EGRNRequest _id="{uuid.uuid1()}" xmlns:dHouse="http://rosreestr.ru/services/v0.1/commons/directories/house" xmlns:dUnitType="http://rosreestr.ru/services/v0.1/commons/directories/unitType" xmlns:dRecieveResultType="http://rosreestr.ru/services/v0.1/commons/directories/recieveResultType" xmlns:DObjectType="http://rosreestr.ru/services/v0.1/commons/directories/regionrf" xmlns:dKindInfo="http://rosreestr.ru/services/v0.1/commons/directories/kindInfo" xmlns:dLandCategory="http://rosreestr.ru/services/v0.1/commons/directories/LandCategory" xmlns:tns="http://rosreestr.ru/services/v0.18/TStatementRequestEGRN" xmlns:obj="http://rosreestr.ru/services/v0.1/commons/TObject" xmlns:subj="http://rosreestr.ru/services/v0.1/commons/Subjects" xmlns:doc="http://rosreestr.ru/services/v0.1/commons/Documents" xmlns:com="http://rosreestr.ru/services/v0.1/commons/Commons" xmlns:vc="http://www.w3.org/2007/XMLSchema-versioning" xmlns:address="http://rosreestr.ru/services/v0.1/commons/Address" xmlns:dObT="http://rosreestr.ru/services/v0.1/commons/directories/objectType" xmlns:stCom="http://rosreestr.ru/services/v0.1/TStatementCommons" xmlns:dObP="http://rosreestr.ru/services/v0.1/commons/directories/objectPurpose" xmlns:dUsT="http://rosreestr.ru/services/v0.1/commons/directories/usageType" xmlns:dReM="http://rosreestr.ru/services/v0.1/commons/directories/receivingMethod" xmlns:dTeZ="http://rosreestr.ru/services/v0.1/commons/directories/terzone" xmlns:dBoO="http://rosreestr.ru/services/v0.1/commons/directories/borderObjectType" xmlns:dDocument="http://rosreestr.ru/services/v0.1/commons/directories/document" xmlns:dAcC="http://rosreestr.ru/services/v0.1/commons/directories/actionCode" xmlns:dSt="http://rosreestr.ru/services/v0.1/commons/directories/statementType" xmlns:dReT="http://rosreestr.ru/services/v0.1/commons/directories/egrnrequesttype" xmlns:dAgr="http://rosreestr.ru/services/v0.1/commons/directories/agreements" xmlns:Sim1="http://rosreestr.ru/services/v0.1/commons/Commons/simple-types" xmlns:dHoP="http://rosreestr.ru/services/v0.1/commons/directories/housingPurpose" xmlns:dRoP="http://rosreestr.ru/services/v0.1/commons/directories/roomPurpose" xmlns:dIObT="http://rosreestr.ru/services/v0.1/commons/directories/interdepobjecttype" xmlns:dCon="http://rosreestr.ru/services/v0.1/commons/directories/contractor" xmlns:dRequestDocument="http://rosreestr.ru/services/v0.1/commons/directories/requestDocument" xmlns:dDeclarantKind="http://rosreestr.ru/services/v0.1/commons/directories/declarantKind" xmlns:dCou="http://rosreestr.ru/services/v0.1/commons/directories/country" xmlns:bCat="http://rosreestr.ru/services/v0.1/commons/directories/benefitCategory" xmlns:dDeKR="http://rosreestr.ru/services/v0.1/commons/directories/declarantKindReg" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://rosreestr.ru/services/v0.18/TStatementRequestEGRN file:///D:/YandexDisk/%D0%92%D0%98%D0%A1/%D0%A1%D0%9F%D0%943%20-%20%D1%81%D0%B5%D1%80%D0%B2%D0%B8%D1%81%20%D0%BF%D1%80%D1%8F%D0%BC%D0%BE%D0%B3%D0%BE%20%D0%B4%D0%BE%D1%81%D1%82%D1%83%D0%BF%D0%B0%20%D0%A0%D0%BE%D1%81%D1%80%D0%B5%D0%B5%D1%81%D1%82%D1%80%D0%B0/03_RequestEGRN_v01_R02%20(%D0%B7%D0%B0%D0%BF%D1%80%D0%BE%D1%81%20%D1%81%D0%B2%D0%B5%D0%B4%D0%B5%D0%BD%D0%B8%D0%B9%20%D0%95%D0%93%D0%A0%D0%9D)/03_RequestEGRN_v01_R02%20(%D0%B7%D0%B0%D0%BF%D1%80%D0%BE%D1%81%20%D1%81%D0%B2%D0%B5%D0%B4%D0%B5%D0%BD%D0%B8%D0%B9%20%D0%95%D0%93%D0%A0%D0%9D)/RequestEGRN_v01.xsd">' + \
        '<tns:header>' + \
        '<stCom:actionCode>659511111112</stCom:actionCode>' + \
        '<stCom:statementType>558630200000</stCom:statementType>' + \
        f'<stCom:creationDate>{datetime.now().strftime("%Y-%m-%dT%H:%M:%S.0")}</stCom:creationDate>' + \
        '</tns:header>' + \
        f'<tns:declarant _id="{uuid.uuid1()}">' + \
        '<subj:other>' + \
        f'<subj:name>{config["name"]}</subj:name>' + \
        f'<subj:inn>{config["inn"]}</subj:inn>' + \
        f'<subj:ogrn>{config["ogrn"]}</subj:ogrn>' + \
        f'<subj:kpp>{config["kpp"]}</subj:kpp>' + \
        f'<subj:regDate>{config["regDate"]}</subj:regDate>' + \
        '</subj:other>' + \
        f'<subj:declarantKind>{config["declarantKind"]}</subj:declarantKind>' + \
        '</tns:declarant>' + \
        '<tns:requestDetails>' + \
        '<tns:requestEGRNDataAction>' + \
        '<tns:extractDataAction>' + \
        '<tns:object>' + \
        f'<obj:objectTypeCode>{config["objectTypeCode"]}</obj:objectTypeCode>' + \
        '<obj:cadastralNumber>' + \
        f'<obj:cadastralNumber>{config["cadastralNumber"]}</obj:cadastralNumber>' + \
        '</obj:cadastralNumber>' + \
        f'</tns:object>' + \
        '<tns:requestType>extractRealty</tns:requestType>' + \
        '</tns:extractDataAction>' + \
        '</tns:requestEGRNDataAction>' + \
        '</tns:requestDetails>' + \
        '<tns:deliveryDetails>' + \
        '<stCom:resultDeliveryMethod>' + \
		'<stCom:recieveResultTypeCode>webService</stCom:recieveResultTypeCode>' + \
		'</stCom:resultDeliveryMethod>' + \
	    '</tns:deliveryDetails>' + \
	    '<tns:statementAgreements>' + \
		'<stCom:persDataProcessingAgreement>01</stCom:persDataProcessingAgreement>' + \
		'<stCom:actualDataAgreement>01</stCom:actualDataAgreement>' + \
	    '</tns:statementAgreements>' + \
        '</tns:EGRNRequest>'

        open(os.path.join(self._workdir, 'app_1.xml'), 'w').write(app_1_xml)
        open(os.path.join(self._workdir, 'request.xml'), 'w').write(request_xml)
        # singn files
        app_1_b64 = base64.b64encode(open(os.path.join(self._workdir, 'app_1.xml'), 'rb').read())
        headers = {'content-type': 'application/text'}
        response = requests.post(self._sign_url, data=app_1_b64, headers=headers, timeout=5)
        assert response.status_code == 200, f'invalid pkcs7 signer response {response.text}'
        app_1_sig_b64 = response.content.decode()
        app_1_sig = base64.b64decode(app_1_sig_b64)
        open(os.path.join(self._workdir, 'app_1.xml.sig'), 'wb').write(app_1_sig)

        request_b64 = base64.b64encode(open(os.path.join(self._workdir, 'request.xml'), 'rb').read())
        headers = {'content-type': 'application/text'}
        response = requests.post(self._sign_url, data=request_b64, headers=headers, timeout=5)
        assert response.status_code == 200, f'invalid pkcs7 signer response {response.text}'
        request_sig_b64 = response.content.decode()
        request_sig = base64.b64decode(request_sig_b64)
        open(os.path.join(self._workdir, 'request.xml.sig'), 'wb').write(request_sig)

        with ZipFile(os.path.join(self._workdir, 'request.zip'), 'w') as zipObj:
            zipObj.write(os.path.join(self._workdir, 'app_1.xml'), 'app_1.xml')
            zipObj.write(os.path.join(self._workdir, 'request.xml'), 'request.xml')
            zipObj.write(os.path.join(self._workdir, 'app_1.xml.sig'), 'app_1.xml.sig')
            zipObj.write(os.path.join(self._workdir, 'request.xml.sig'), 'request.xml.sig')
        return os.path.join(self._workdir, 'request.zip')


# builder = EgrzBuilder(sign_url='http://mogt-ml:8080/v1/signer/pkcs7/samara', workdir='1')
# conf = {
#     'requestType'    : '111',
#     'cadastralNumber': '111',
#     'name'           : '111',
#     'inn'            : '111',
#     'ogrn'           : '111',
#     'kpp'            : '111',
#     'regDate'        : '111',
#     'declarantKind'  : '111',
#     'objectTypeCode' : '111'
# }
# print(builder.build_zip(config=conf))