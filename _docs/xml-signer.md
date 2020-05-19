# Smev-3 client: xml-signer

*Service location:* `./xml-signer`

*Service purpose:* converting messages to smev-3.X format (including versions 1.1, 1.2, 1.3), signing messages using JCP Cryptopro or Open SSL with GOST-Engine

*config files:* 

- `./xml-signer/*.inc` - smev message envelope templates
- `./xml-signer/config.json` - certificate aliases and passwords
- `./xml-signer/log4j.properties` - logging config

## API

- **POST** `/api/v1/{sert_public_alias}`
  *request*

  ```json
  {
      "xml": string,
      "id": string,
      "to": string,
      "msgType": string,
      "tagForSign": string,
      "attachments":[
          "file_1",
          "file_2",
          ..
          "file_n"
      ]
  }
  ```

  *response*

  ```json
  {
      "xml": string,
      "id": string
  }
  ```

  *where:*

  - `xml` - smev xml teamplate e.g:

    ```xml
    <tns:ESIADataVerifyRequest xmlns:tns="urn://mincomsvyaz/esia/uprid/1.4.2" xmlns:ns2="urn://mincomsvyaz/esia/commons/rg_sevices_types/1.4.2">
        <tns:RoutingCode>TESIA</tns:RoutingCode>
        <tns:passportSeries>1111</tns:passportSeries>
        <tns:passportNumber>111111</tns:passportNumber>
        <tns:lastName>Тестов</tns:lastName>
        <tns:firstName>Тест</tns:firstName>
        <tns:middleName>Тестович</tns:middleName>
        <tns:snils>229-785-346 20</tns:snils>
    </tns:ESIADataVerifyRequest>
    ```

  - **`id`** - uuid

    - "0" - to generate new uuid
    - "uuid" - use target uuid e.g. `b778f4a4-6f47-11ea-a59b-239621d4fae8`.

  - **`msgType`** - SMEV-3 mesage type `[SendRequestRequest, GetResponseRequest, AckRequest]`  

  - **`tagForSign`** - XML tag ID to sign `[SIGNED_BY_CONSUMER, SIGNED_BY_CALLER]`

    *`tagForSign ` property this property depends on who you are in relation to the message broker smav 3. If you accept something, then you CALLER but if you answer something - you are CONSUMER. The values of these tags are set in message templates `.inc`. The table below shows the correspondence between tags and standard message types.*

    | Message             | Tag                |
    | ------------------- | ------------------ |
    | AckRequest          | SIGNED_BY_CALLER   |
    | GetRequestRequest   | SIGNED_BY_CALLER   |
    | GetResponseRequest  | SIGNED_BY_CALLER   |
    | SendRequestRequest  | SIGNED_BY_CONSUMER |
    | SendResponseRequest | SIGNED_BY_CONSUMER |

    *P.s. It is very difficult to understand and you can go crazy when you try to delve into the logic of these tags and message types. The whole table above is valid only for half of the cases - if you are a client for the smev 3 broker. In the event that you are making a service for SMEV 3 that is, simply put, you are a queuing worker, you must mirror these tags.*  

    *Different types of messages also require a different set of input parameters. For a better understanding, you should pay attention to the official documentation for SMEV 3. Below I will give a table of correspondence between messages and input parameters. Only `id`, `magType` and `tagForSign` are required*

    | Message             | Params required [ optional params ] |
    | ------------------- | ----------------------------------- |
    | AckRequest          |                                     |
    | GetRequestRequest   | xml                                 |
    | GetResponseRequest  | [ xml ]                             |
    | SendRequestRequest  | xml, [ attachments ]                |
    | SendResponseRequest | xml, to, [ attachments ]            |

## Configuration

Define your crypto certificates and aliases in `config.json`

```json
{
    "certs":
    {
        "org_a":
        {
            "alias":"org_isogd_2020",
            "password":"11111111"
        },
        "grb_b":
        {
            "alias":"org_rgis_2021",
            "password":"22222222"
        }
    }
}

```

## Examples

### Example 1

```json
POST localhost:5000/api/v1/org_a/
Request 1:
{
    "id": "0",
    "msgType": "GetResponseRequest",
    "tagForSign": "SIGNED_BY_CALLER"
}

Response 1:
{
    "id": "f2458bb7-9962-11ea-b5b5-d5b949f549e9",
    "xml": "<SOAP-ENV:Envelope xmlns:SOAP-ENV=\"http://schemas.xmlsoap.org/soap/envelope/\"><SOAP-ENV:Header/><SOAP-ENV:Body><ns2:GetResponseRequest xmlns=\"urn://x-artefacts-smev-gov-ru/services/message-exchange/types/basic/1.2\" xmlns:ns2=\"urn://x-artefacts-smev-gov-ru/services/message-exchange/types/1.2\" xmlns:ns3=\"urn://x-artefacts-smev-gov-ru/services/message-exchange/types/faults/1.2\">\n    <ns2:MessageTypeSelector xmlns=\"urn://x-artefacts-smev-gov-ru/services/message-exchange/types/1.2\" xmlns:ns2=\"urn://x-artefacts-smev-gov-ru/services/message-exchange/types/basic/1.2\" Id=\"SIGNED_BY_CALLER\"><ns2:Timestamp>2020-05-19T02:54:43.871+03:00</ns2:Timestamp></ns2:MessageTypeSelector>\n    <ns2:CallerInformationSystemSignature><ds:Signature xmlns:ds=\"http://www.w3.org/2000/09/xmldsig#\"><ds:SignedInfo><ds:CanonicalizationMethod Algorithm=\"http://www.w3.org/2001/10/xml-exc-c14n#\"/><ds:SignatureMethod Algorithm=\"urn:ietf:params:xml:ns:cpxmlsec:algorithms:gostr34102012-gostr34112012-256\"/><ds:Reference URI=\"#SIGNED_BY_CALLER\"><ds:Transforms><ds:Transform Algorithm=\"http://www.w3.org/2001/10/xml-exc-c14n#\"/><ds:Transform Algorithm=\"urn://smev-gov-ru/xmldsig/transform\"/></ds:Transforms><ds:DigestMethod Algorithm=\"urn:ietf:params:xml:ns:cpxmlsec:algorithms:gostr34112012-256\"/><ds:DigestValue>T8ADUFLnflgM...</ds:DigestValue></ds:Reference></ds:SignedInfo><ds:SignatureValue>TAARdoD...</ds:SignatureValue><ds:KeyInfo><ds:X509Data><ds:X509Certificate>MIIKaDCCChWgAwI...</ds:X509Certificate></ds:X509Data></ds:KeyInfo></ds:Signature></ns2:CallerInformationSystemSignature>\n</ns2:GetResponseRequest></SOAP-ENV:Body></SOAP-ENV:Envelope>"
}
```

### Example 2

```js
POST localhost:5000/api/v1/org_a/
Request 1:
{
    "xml": "<egrz:DocumentsVolumeRequest xmlns:egrz=\"urn://x-artefacts-gis-ergz-documents-volume/2.0.0\" xmlns:egrzt=\"urn://x-artefacts-gis-ergz-types/2.0.0\">  <egrzt:PrintOutNumber>5a696d88-9ea0-43f5-8f74-c68e3632ce7c</egrzt:PrintOutNumber>  <egrzt:VolumeID>4ffa8c98-6392-4d3b-bf98-5ef7f5ec6d3b.zip.002</egrzt:VolumeID></egrz:DocumentsVolumeRequest>",
    "id": "0",
    "msgType": "SendRequestRequest",
    "tagForSign": "SIGNED_BY_CONSUMER"
}

Response 1:
{
    "id": "4a4fff78-9963-11ea-b5b5-9fad6bf46af3",
    "xml": "<SOAP-ENV:Envelope xmlns:SOAP-ENV=\"http://schemas.xmlsoap.org/soap/envelope/\"><SOAP-ENV:Header/><SOAP-ENV:Body><ns2:SendRequestRequest xmlns=\"urn://x-artefacts-smev-gov-ru/services/message-exchange/types/basic/1.2\" xmlns:ns2=\"urn://x-artefacts-smev-gov-ru/services/message-exchange/types/1.2\" xmlns:ns3=\"urn://x-artefacts-smev-gov-ru/services/message-exchange/types/faults/1.2\">\n    <ns:SenderProvidedRequestData xmlns=\"urn://x-artefacts-smev-gov-ru/services/message-exchange/types/1.2\" xmlns:ns=\"urn://x-artefacts-smev-gov-ru/services/message-exchange/types/1.2\" xmlns:ns2=\"urn://x-artefacts-smev-gov-ru/services/message-exchange/types/basic/1.2\" Id=\"SIGNED_BY_CONSUMER\">\n        <ns:MessageID>4a4fff78-9963-11ea-b5b5-9fad6bf46af3</ns:MessageID>\n        <ns2:MessagePrimaryContent><egrz:DocumentsVolumeRequest xmlns:egrz=\"urn://x-artefacts-gis-ergz-documents-volume/2.0.0\" xmlns:egrzt=\"urn://x-artefacts-gis-ergz-types/2.0.0\">  <egrzt:PrintOutNumber>5a696d88-9ea0-43f5-8f74-c68e3632ce7c</egrzt:PrintOutNumber>  <egrzt:VolumeID>4ffa8c98-6392-4d3b-bf98-5ef7f5ec6d3b.zip.002</egrzt:VolumeID></egrz:DocumentsVolumeRequest></ns2:MessagePrimaryContent>\n    </ns:SenderProvidedRequestData>\n    <ns2:CallerInformationSystemSignature><ds:Signature xmlns:ds=\"http://www.w3.org/2000/09/xmldsig#\"><ds:SignedInfo><ds:CanonicalizationMethod Algorithm=\"http://www.w3.org/2001/10/xml-exc-c14n#\"/><ds:SignatureMethod Algorithm=\"urn:ietf:params:xml:ns:cpxmlsec:algorithms:gostr34102012-gostr34112012-256\"/><ds:Reference URI=\"#SIGNED_BY_CONSUMER\"><ds:Transforms><ds:Transform Algorithm=\"http://www.w3.org/2001/10/xml-exc-c14n#\"/><ds:Transform Algorithm=\"urn://smev-gov-ru/xmldsig/transform\"/></ds:Transforms><ds:DigestMethod Algorithm=\"urn:ietf:params:xml:ns:cpxmlsec:algorithms:gostr34112012-256\"/><ds:DigestValue>kYx2...</ds:DigestValue></ds:Reference></ds:SignedInfo><ds:SignatureValue>NcG+...</ds:SignatureValue><ds:KeyInfo><ds:X509Data><ds:X509Certificate>MIIKa...</ds:X509Certificate></ds:X509Data></ds:KeyInfo></ds:Signature></ns2:CallerInformationSystemSignature>\n</ns2:SendRequestRequest></SOAP-ENV:Body></SOAP-ENV:Envelope>"
}
```

### Example 3

```json
POST localhost:5000/api/v1/org_a/
Request 1:
{
    "id": "acbc78b7-9466-11ea-b8f2-637c98c72989",
    "msgType": "AckRequest",
    "tagForSign": "SIGNED_BY_CALLER"
}

Response 1:
{
    "id": "acbc78b7-9466-11ea-b8f2-637c98c72989",
    "xml": "<SOAP-ENV:Envelope xmlns:SOAP-ENV=\"http://schemas.xmlsoap.org/soap/envelope/\"><SOAP-ENV:Header/><SOAP-ENV:Body><ns2:AckRequest xmlns=\"urn://x-artefacts-smev-gov-ru/services/message-exchange/types/basic/1.2\" xmlns:ns2=\"urn://x-artefacts-smev-gov-ru/services/message-exchange/types/1.2\" xmlns:ns3=\"urn://x-artefacts-smev-gov-ru/services/message-exchange/types/faults/1.2\">\n    <ns2:AckTargetMessage xmlns=\"urn://x-artefacts-smev-gov-ru/services/message-exchange/types/1.2\" xmlns:ns2=\"urn://x-artefacts-smev-gov-ru/services/message-exchange/types/basic/1.2\" Id=\"SIGNED_BY_CALLER\" accepted=\"true\">acbc78b7-9466-11ea-b8f2-637c98c72989</ns2:AckTargetMessage>\n    <ns2:CallerInformationSystemSignature><ds:Signature xmlns:ds=\"http://www.w3.org/2000/09/xmldsig#\"><ds:SignedInfo><ds:CanonicalizationMethod Algorithm=\"http://www.w3.org/2001/10/xml-exc-c14n#\"/><ds:SignatureMethod Algorithm=\"urn:ietf:params:xml:ns:cpxmlsec:algorithms:gostr34102012-gostr34112012-256\"/><ds:Reference URI=\"#SIGNED_BY_CALLER\"><ds:Transforms><ds:Transform Algorithm=\"http://www.w3.org/2001/10/xml-exc-c14n#\"/><ds:Transform Algorithm=\"urn://smev-gov-ru/xmldsig/transform\"/></ds:Transforms><ds:DigestMethod Algorithm=\"urn:ietf:params:xml:ns:cpxmlsec:algorithms:gostr34112012-256\"/><ds:DigestValue>cf3...</ds:DigestValue></ds:Reference></ds:SignedInfo><ds:SignatureValue>M3+...</ds:SignatureValue><ds:KeyInfo><ds:X509Data><ds:X509Certificate>MII...</ds:X509Certificate></ds:X509Data></ds:KeyInfo></ds:Signature></ns2:CallerInformationSystemSignature>\n</ns2:AckRequest></SOAP-ENV:Body></SOAP-ENV:Envelope>"
}
```

