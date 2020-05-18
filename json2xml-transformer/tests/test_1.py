from starlette.testclient import TestClient
import sys
sys.path.append('..')
from server import app

client = TestClient(app)

def test_xsd_processor():
    response = client.post(
        "/api/v1/FNSVipULRequest",
        json={
                "ЗапросЮЛ": {
                    "ОГРН": "1027700070518"
                },
                "ИдДок": "3"
            },
    )
    assert response.status_code == 200
    assert response.json() == {"xml": "<ns0:FNSVipULRequest xmlns:ns0=\"urn://x-artefacts-fns-vipul-tosmv-ru/311-14/4.0.6\" ИдДок=\"3\"><ns0:ЗапросЮЛ><ns0:ОГРН>1027700070518</ns0:ОГРН></ns0:ЗапросЮЛ></ns0:FNSVipULRequest>"}

def test_xsd_processor_wrong_elemrnt():
    response = client.post(
        "/api/v1/FNSVipULRequest",
        json={
                "ЗапросЮЛ": {
                    "ОГРН": "1027700070518"
                },
                "ИдДок": "3"
            },
    )
    assert response.status_code == 400
    assert response.json() == { "detail": "No such element_type FNSVipULReques." }