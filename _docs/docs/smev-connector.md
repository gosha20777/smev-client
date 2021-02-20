# Smev-3 client: smev-connector

*Service location:* `./smev-connector`

*Service purpose:* connect and communicate with smev 3 endpoints

*config files:* 

- `./smev-connector/config.json` - smev-3 endpoint definitions
- `./json2xml-transformer/log-config.yaml` - logging config

## API

- **POST** `/api/v1/send/{smev_host_alias}`
  *request*

  ```json
  {
      "xml": str,
      "id": str (uuid)
  }
  ```

  *response*

  ```json
  {
      "xml": str
      "id": str (uuid),
  	"success": bool
  }
  ```
  

*where*

  - `xml` - xml message
  - `id` - id of the source message (e.g. if you send a GetResponseRequest id will equals OriginalMesageId, else will be same as MesageId of request). The request id must be equals MesageId in xml.
  - `success` - transaction success (True, False)

`Note:` *In addition to direct requests, the connector also performs background requests to the smev-3 queue. Such requests are made in parallel and independently for different server endpoints.*

## Configuration

1. Define your smev 3 endpoints and it's schemes versions in `config.json` file. E.g.:

```
{
    "smev-test-1-1": {
        "url": "http://smev3-n0.test.gosuslugi.ru:7500/smev/v1.1/ws?wsd",
        "version": 1.1,
        "survey_period": 2,
        "tocken_refresh_period": 5,
        "connet_timeout": 3
    },
    "smev-test-1-2": {
        "url": "http://smev3-n0.test.gosuslugi.ru:7500/smev/v1.2/ws?wsd",
        "version": 1.2,
        "survey_period": 5,
        "tocken_refresh_period": 5,
        "connet_timeout": 3
    } 
}
```

2. If you don't default use database in docker - define the environment variables from `app.conf` file.

## Usage examples

*There are two examples of Ack message. That's why they are short. in a real situation, you can send any type of message using this interface. Remember that there are background handlers for processing the output queue. Nevertheless, no one bothers you to send a message to receive an answer yourself. In this case, this message will not be added as a response to the task database. You must process this message and update the corresponding task statuses manually.*

### Example 1

```json
POST localhost:5000/api/v1/FNSVipULRequest/
Request:
{
    "id": "acbc78b7-9466-11ea-b8f2-637c98c72989",
    "xml": "<SOAP-ENV:Envelope xmlns:SOAP-ENV=\"http://schemas.xmlsoap.org/soap/envelope/\"><SOAP-ENV:Header/><SOAP-ENV:Body><ns2:AckRequest xmlns=\"urn://x-artefacts-smev-gov-ru/services/message-exchange/types/basic/1.2\" xmlns:ns2=\"urn://x-artefacts-smev-gov-ru/services/message-exchange/types/1.2\" xmlns:ns3=\"urn://x-artefacts-smev-gov-ru/services/message-exchange/types/faults/1.2\">\n    <ns2:AckTargetMessage xmlns=\"urn://x-artefacts-smev-gov-ru/services/message-exchange/types/1.2\" xmlns:ns2=\"urn://x-artefacts-smev-gov-ru/services/message-exchange/types/basic/1.2\" Id=\"SIGNED_BY_CALLER\" accepted=\"true\">acbc78b7-9466-11ea-b8f2-637c98c72989</ns2:AckTargetMessage>\n    <ns2:CallerInformationSystemSignature><ds:Signature xmlns:ds=\"http://www.w3.org/2000/09/xmldsig#\"><ds:SignedInfo><ds:CanonicalizationMethod Algorithm=\"http://www.w3.org/2001/10/xml-exc-c14n#\"/><ds:SignatureMethod Algorithm=\"urn:ietf:params:xml:ns:cpxmlsec:algorithms:gostr34102012-gostr34112012-256\"/><ds:Reference URI=\"#SIGNED_BY_CALLER\"><ds:Transforms><ds:Transform Algorithm=\"http://www.w3.org/2001/10/xml-exc-c14n#\"/><ds:Transform Algorithm=\"urn://smev-gov-ru/xmldsig/transform\"/></ds:Transforms><ds:DigestMethod Algorithm=\"urn:ietf:params:xml:ns:cpxmlsec:algorithms:gostr34112012-256\"/><ds:DigestValue>cf35Axu11YakJi02iRPwz+.......</ds:DigestValue></ds:Reference></ds:SignedInfo><ds:SignatureValue>gXCel9i8unE5Vt4MDCovDbc21fYMqx4RjOdUXS13yTKupHMe0yqvxaibtQz5rD11Hz/Eh0DPLtBsc5qZ1Gvx9g==</ds:SignatureValue><ds:KeyInfo><ds:X509Data><ds:X509Certificate>MIIKaDCCChWgAwIBAgIKVyUDbwABAAPvRjAKBggqhQMHAQEDAjCCAUExGDAWBgUqhQNkARINMTAyMTYwMjg1NTI2MjEaMBgGCCqF....</ds:X509Certificate></ds:X509Data></ds:KeyInfo></ds:Signature></ns2:CallerInformationSystemSignature>\n</ns2:AckRequest></SOAP-ENV:Body></SOAP-ENV:Envelope>"
}

Response:
{
    "id": "acbc78b7-9466-11ea-b8f2-637c98c72989",
    "success": fasle,
    "xml": "<soap:Envelope xmlns:soap=\"http://schemas.xmlsoap.org/soap/envelope/\"><soap:Body><soap:Fault><faultcode>soap:Server</faultcode><faultstring>Сообщение acbc78b7-9466-11ea-b8f2-637c98c72989 не найдено среди неподтверждённых.</faultstring><detail><ns3:TargetMessageIsNotFound xmlns:xsi=\"http://www.w3.org/2001/XMLSchema-instance\" xmlns:ns3=\"urn://x-artefacts-smev-gov-ru/services/message-exchange/types/faults/1.2\" xmlns:ns2=\"urn://x-artefacts-smev-gov-ru/services/message-exchange/types/1.2\" xmlns=\"urn://x-artefacts-smev-gov-ru/services/message-exchange/types/basic/1.2\" xsi:type=\"SmevFault\"><Code>tsmev3:PRODUCTION_AREA:TSMEV3_CORE1 : TR:SYNC:DAS:4</Code><Description>SMEV-501:Сообщение acbc78b7-9466-11ea-b8f2-637c98c72989 не найдено среди неподтверждённых.</Description></ns3:TargetMessageIsNotFound></detail></soap:Fault></soap:Body></soap:Envelope>"
} (tocken expired)
```

### Example 2

```json
POST localhost:5000/api/v1/FNSVipULRequest/
Request:
{
    "id": "acbc78b7-9466-11ea-b8f2-637c98c72989",
    "xml": "<SOAP-ENV:Envelope xmlns:SOAP-ENV=\"http://schemas.xmlsoap.org/soap/envelope/\"><SOAP-ENV:Header/><SOAP-ENV:Body><ns2:AckRequest xmlns=\"urn://x-artefacts-smev-gov-ru/services/message-exchange/types/basic/1.2\" xmlns:ns2=\"urn://x-artefacts-smev-gov-ru/services/message-exchange/types/1.2\" xmlns:ns3=\"urn://x-artefacts-smev-gov-ru/services/message-exchange/types/faults/1.2\">\n    <ns2:AckTargetMessage xmlns=\"urn://x-artefacts-smev-gov-ru/services/message-exchange/types/1.2\" xmlns:ns2=\"urn://x-artefacts-smev-gov-ru/services/message-exchange/types/basic/1.2\" Id=\"SIGNED_BY_CALLER\" accepted=\"true\">acbc78b7-9466-11ea-b8f2-637c98c72989</ns2:AckTargetMessage>\n    <ns2:CallerInformationSystemSignature><ds:Signature xmlns:ds=\"http://www.w3.org/2000/09/xmldsig#\"><ds:SignedInfo><ds:CanonicalizationMethod Algorithm=\"http://www.w3.org/2001/10/xml-exc-c14n#\"/><ds:SignatureMethod Algorithm=\"urn:ietf:params:xml:ns:cpxmlsec:algorithms:gostr34102012-gostr34112012-256\"/><ds:Reference URI=\"#SIGNED_BY_CALLER\"><ds:Transforms><ds:Transform Algorithm=\"http://www.w3.org/2001/10/xml-exc-c14n#\"/><ds:Transform Algorithm=\"urn://smev-gov-ru/xmldsig/transform\"/></ds:Transforms><ds:DigestMethod Algorithm=\"urn:ietf:params:xml:ns:cpxmlsec:algorithms:gostr34112012-256\"/><ds:DigestValue>cf35Axu11YakJi02iRPwz+tvWCMV.......</ds:DigestValue></ds:Reference></ds:SignedInfo><ds:SignatureValue>gXCel9i8unE5Vt4MDCovDbc21fYMqx4RjOdUXS13yTKupHMe0yqvxaibtQz5rD11Hz/Eh0DPLtBsc5qZ1Gvx9g==</ds:SignatureValue><ds:KeyInfo><ds:X509Data><ds:X509Certificate>MIIKaDCCChWgAwIBAgIKVyUDbwABAAPvRjAKBggqhQMHAQEDAjCCAUExGDAWBgUqhQNkARINMTAyMTYwMjg1NTI2MjEaMBgGCCqF....</ds:X509Certificate></ds:X509Data></ds:KeyInfo></ds:Signature></ns2:CallerInformationSystemSignature>\n</ns2:AckRequest></SOAP-ENV:Body></SOAP-ENV:Envelope>"
}

Response:
{
    "id": "acbc78b7-9466-11ea-b8f2-637c98c72989",
    "success": true,
    "xml": "<soap:Envelope xmlns:soap=\"http://schemas.xmlsoap.org/soap/envelope/\"><soap:Body></soap:Body></soap:Envelope>"
} (task is finised)
```