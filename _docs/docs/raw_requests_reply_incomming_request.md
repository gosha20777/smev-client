### Make a Replay

#### 1: get incoming requests

- GET `localhost:8080/v1/records/worker`
  *get all chains of messages where*
  - `(GetRequestRequest != null && GetRequestResponse != null && AckRequest == null)`
  - `id` - message id of `GetRequestResponse`

```json
<-
[
    {
        "id": "047b500c-04a4-11eb-af32-fa163eff7bf8",
        "mesages": [
            "GetRequestRequest",
            "GetRequestResponse"
        ],
        "date": "2020-10-05T13:03:50.205058",
        "communication_type": "urn://gisogd73/rs/1.0.0"
    }
    ...
]
```

#### 2: get GetRequestResponse of mesage and parse it

- GET `localhost:8080/v1/record/047b500c-04a4-11eb-af32-fa163eff7bf8/GetRequestResponse`

```json
<-
{
    "id": "047b500c-04a4-11eb-af32-fa163eff7bf8",
    "xml": "<soap:Envelope xmlns:soap=\"http://schemas.xmlsoap.org/soap/envelope/\"><soap:Body><ns2:GetRequestResponse xmlns=\"urn://x-artefacts-smev-gov-ru/services/message-exchange/types/basic/1.1\" xmlns:ns2=\"urn://x-artefacts-smev-gov-ru/services/message-exchange/types/1.1\" xmlns:ns3=\"urn://x-artefacts-smev-gov-ru/services/message-exchange/types/faults/1.1\"><ns2:RequestMessage><ns2:Request Id=\"SIGNED_BY_SMEV\"><ns2:SenderProvidedRequestData Id=\"SIGNED_BY_CALLER\"><ns2:MessageID>047b500c-04a4-11eb-af32-fa163eff7bf8</ns2:MessageID><ns2:TransactionCode>b12d52e6-04a3-11eb-8b86-fa163ee4b849</ns2:TransactionCode><MessagePrimaryContent><tns:Request xmlns:tns=\"urn://gisogd73/gpzu/1.0.0\" xmlns=\"urn://x-artefacts-smev-gov-ru/services/message-exchange/types/1.2\" xmlns:com=\"urn://gisogd73/commons/1.0.0\" xmlns:ns2=\"urn://x-artefacts-smev-gov-ru/services/message-exchange/types/basic/1.2\" xmlns:ns3=\"urn://x-artefacts-smev-gov-ru/services/message-exchange/types/faults/1.2\"><tns:OKTMO>73000000</tns:OKTMO><tns:service><tns:CurrentDate>2020-10-02</tns:CurrentDate><tns:UserType>PERSON_RF</tns:UserType><tns:CaseNumber>73389397</tns:CaseNumber><tns:ServiceCode>7300000020000108239</tns:ServiceCode><tns:GroupID>7300000000170830765</tns:GroupID>\n</tns:service><tns:Panel_FL><tns:sur>Сидоренко</tns:sur><tns:nam>Петр</tns:nam><tns:pat>Иванович</tns:pat><tns:snils>01000030623</tns:snils><tns:home_addr><com:address>450077, Респ. Башкортостан, г. Уфа, ул. Ленина, д. 1, кв. 1</com:address><com:index>450077</com:index><com:region>Башкортостан республика</com:region><com:city>Уфа</com:city><com:street>Ленина</com:street><com:house>1</com:house><com:apartment>1</com:apartment>\n</tns:home_addr><tns:fl_post_address><com:address>115533, г. Москва, пр-кт. Андропова, д. 6, стр. 5, кв. 7</com:address><com:index>115533</com:index><com:region>Москва город</com:region><com:street>Андропова</com:street><com:house>6</com:house><com:building2>5</com:building2><com:apartment>7</com:apartment>\n</tns:fl_post_address><tns:fl_phone>+7(342)222-43-41</tns:fl_phone><tns:fl_email>el@Mail.ru</tns:fl_email>\n</tns:Panel_FL><tns:Panel_passport><tns:docSeries>5555</tns:docSeries><tns:docNumber>123455</tns:docNumber><tns:docIssued>РУВД</tns:docIssued><tns:docDate>1993-03-26</tns:docDate>\n</tns:Panel_passport><tns:Panel_Land_info><tns:kadastr_number>00:00:000000:00</tns:kadastr_number><tns:square>0</tns:square><tns:type_address>Address</tns:type_address><tns:stead_address><com:address>460000, обл. Оренбургская, г. Оренбург, пр-кт. Гагарина</com:address><com:index>460000</com:index><com:region>Оренбургская область</com:region><com:city>Оренбург</com:city><com:street>Гагарина</com:street>\n</tns:stead_address>\n</tns:Panel_Land_info><tns:Panel_Get_result><tns:radio_sposob>Department</tns:radio_sposob>\n</tns:Panel_Get_result>\n</tns:Request></MessagePrimaryContent><RefAttachmentHeaderList><RefAttachmentHeader><uuid>1b0d3a3a-0616-403f-946b-1c14ac384239</uuid><Hash>3RNKfXjGXT4NQrjmmm7b6CEOrS044njPPq2U7HQ+EGE=</Hash><MimeType>application/zip</MimeType><SignaturePKCS7><xop:Include xmlns:xop=\"http://www.w3.org/2004/08/xop/include\" href=\"cid:d0abc6a3-f82c-46fa-a2cf-6b1b8b78c460-652793@urn%3A%2F%2Fx-artefacts-smev-gov-ru%2Fservices%2Fmessage-exchange%2Ftypes%2Fbasic%2F1.1\"/></SignaturePKCS7></RefAttachmentHeader></RefAttachmentHeaderList></ns2:SenderProvidedRequestData><ns2:MessageMetadata><ns2:MessageId>047b500c-04a4-11eb-af32-fa163eff7bf8</ns2:MessageId><ns2:MessageType>REQUEST</ns2:MessageType><ns2:Sender><ns2:Mnemonic>MNSV05</ns2:Mnemonic><ns2:HumanReadableName>ЕПГУ (svcdev)</ns2:HumanReadableName></ns2:Sender><ns2:SendingTimestamp>2020-10-02T14:40:08.000+03:00</ns2:SendingTimestamp><ns2:DestinationName>unknown</ns2:DestinationName><ns2:Recipient><ns2:Mnemonic>03UD02</ns2:Mnemonic><ns2:HumanReadableName>ГИС ОГД</ns2:HumanReadableName></ns2:Recipient><ns2:SupplementaryData><ns2:DetectedContentTypeName>not detected</ns2:DetectedContentTypeName><ns2:InteractionType>NotDetected</ns2:InteractionType></ns2:SupplementaryData><ns2:DeliveryTimestamp>2020-10-06T12:51:26.416+03:00</ns2:DeliveryTimestamp><ns2:Status>responseIsDelivered</ns2:Status></ns2:MessageMetadata><FSAttachmentsList><FSAttachment><uuid>1b0d3a3a-0616-403f-946b-1c14ac384239</uuid><UserName>3MSVWESNTfOjxYCyl1W4cuWbmMeCs9</UserName><Password>Y3oxXKp4PuStEFPWjgwL1qyX6rmGXE</Password><FileName>/SignedContent.zip</FileName></FSAttachment></FSAttachmentsList><ns2:ReplyTo>eyJzaWQiOjMxNzE0LCJtaWQiOiIwNDdiNTAwYy0wNGE0LTExZWItYWYzMi1mYTE2M2VmZjdiZjgiLCJ0Y2QiOiJiMTJkNTJlNi0wNGEzLTExZWItOGI4Ni1mYTE2M2VlNGI4NDkiLCJlb2wiOjAsInNsYyI6Imdpc29nZDczX2dwenVfMS4wLjBfUmVxdWVzdCIsIm1ubSI6Ik1OU1YwNSJ9</ns2:ReplyTo></ns2:Request><ns2:SMEVSignature><ds:Signature xmlns:ds=\"http://www.w3.org/2000/09/xmldsig#\"><ds:SignedInfo><ds:CanonicalizationMethod Algorithm=\"http://www.w3.org/2001/10/xml-exc-c14n#\"/><ds:SignatureMethod Algorithm=\"urn:ietf:params:xml:ns:cpxmlsec:algorithms:gostr34102012-gostr34112012-256\"/><ds:Reference URI=\"#SIGNED_BY_SMEV\"><ds:Transforms><ds:Transform Algorithm=\"http://www.w3.org/2001/10/xml-exc-c14n#\"/><ds:Transform Algorithm=\"urn://smev-gov-ru/xmldsig/transform\"/></ds:Transforms><ds:DigestMethod Algorithm=\"urn:ietf:params:xml:ns:cpxmlsec:algorithms:gostr34112012-256\"/><ds:DigestValue>dBqVs+Alv+Lwhuj6+7h/eQzouPT64VHgjOVT5n3b30Y=</ds:DigestValue></ds:Reference></ds:SignedInfo><ds:SignatureValue>jEDI/eO947HjY4KRYdFrvlevJ/pG/d9DYfefFHNhRKrU5HMZaEh2WsntDLD73si3UUbI07WgqsVZ/eKSM/ttkQ==</ds:SignatureValue><ds:KeyInfo><ds:X509Data><ds:X509Certificate>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</ds:X509Certificate></ds:X509Data></ds:KeyInfo></ds:Signature></ns2:SMEVSignature></ns2:RequestMessage></ns2:GetRequestResponse></soap:Body></soap:Envelope>"
}
```

or get xml

- GET `localhost:8090/v1/record/047b500c-04a4-11eb-af32-fa163eff7bf8/GetRequestResponse/xml`

```xml
<-
<soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
    <soap:Body>
        <ns2:GetRequestResponse xmlns="urn://x-artefacts-smev-gov-ru/services/message-exchange/types/basic/1.1" xmlns:ns2="urn://x-artefacts-smev-gov-ru/services/message-exchange/types/1.1" xmlns:ns3="urn://x-artefacts-smev-gov-ru/services/message-exchange/types/faults/1.1">
            <ns2:RequestMessage>
                <ns2:Request Id="SIGNED_BY_SMEV">
                    <ns2:SenderProvidedRequestData Id="SIGNED_BY_CALLER">
                        <ns2:MessageID>047b500c-04a4-11eb-af32-fa163eff7bf8</ns2:MessageID>
                        <ns2:TransactionCode>b12d52e6-04a3-11eb-8b86-fa163ee4b849</ns2:TransactionCode>
                        <MessagePrimaryContent>
                            <tns:Request xmlns:tns="urn://gisogd73/gpzu/1.0.0" xmlns="urn://x-artefacts-smev-gov-ru/services/message-exchange/types/1.2" xmlns:com="urn://gisogd73/commons/1.0.0" xmlns:ns2="urn://x-artefacts-smev-gov-ru/services/message-exchange/types/basic/1.2" xmlns:ns3="urn://x-artefacts-smev-gov-ru/services/message-exchange/types/faults/1.2">
                                <tns:OKTMO>73000000</tns:OKTMO>
                                <tns:service>
                                    <tns:CurrentDate>2020-10-02</tns:CurrentDate>
                                    <tns:UserType>PERSON_RF</tns:UserType>
                                    <tns:CaseNumber>73389397</tns:CaseNumber>
                                    <tns:ServiceCode>7300000020000108239</tns:ServiceCode>
                                    <tns:GroupID>7300000000170830765</tns:GroupID>
                                </tns:service>
                                <tns:Panel_FL>
                                    <tns:sur>Сидоренко</tns:sur>
                                    <tns:nam>Петр</tns:nam>
                                    <tns:pat>Иванович</tns:pat>
                                    <tns:snils>01000030623</tns:snils>
                                    <tns:home_addr>
                                        <com:address>450077, Респ. Башкортостан, г. Уфа, ул. Ленина, д. 1, кв. 1</com:address>
                                        <com:index>450077</com:index>
                                        <com:region>Башкортостан республика</com:region>
                                        <com:city>Уфа</com:city>
                                        <com:street>Ленина</com:street>
                                        <com:house>1</com:house>
                                        <com:apartment>1</com:apartment>
                                    </tns:home_addr>
                                    <tns:fl_post_address>
                                        <com:address>115533, г. Москва, пр-кт. Андропова, д. 6, стр. 5, кв. 7</com:address>
                                        <com:index>115533</com:index>
                                        <com:region>Москва город</com:region>
                                        <com:street>Андропова</com:street>
                                        <com:house>6</com:house>
                                        <com:building2>5</com:building2>
                                        <com:apartment>7</com:apartment>
                                    </tns:fl_post_address>
                                    <tns:fl_phone>+7(342)222-43-41</tns:fl_phone>
                                    <tns:fl_email>el@Mail.ru</tns:fl_email>
                                </tns:Panel_FL>
                                <tns:Panel_passport>
                                    <tns:docSeries>5555</tns:docSeries>
                                    <tns:docNumber>123455</tns:docNumber>
                                    <tns:docIssued>РУВД</tns:docIssued>
                                    <tns:docDate>1993-03-26</tns:docDate>
                                </tns:Panel_passport>
                                <tns:Panel_Land_info>
                                    <tns:kadastr_number>00:00:000000:00</tns:kadastr_number>
                                    <tns:square>0</tns:square>
                                    <tns:type_address>Address</tns:type_address>
                                    <tns:stead_address>
                                        <com:address>460000, обл. Оренбургская, г. Оренбург, пр-кт. Гагарина</com:address>
                                        <com:index>460000</com:index>
                                        <com:region>Оренбургская область</com:region>
                                        <com:city>Оренбург</com:city>
                                        <com:street>Гагарина</com:street>
                                    </tns:stead_address>
                                </tns:Panel_Land_info>
                                <tns:Panel_Get_result>
                                    <tns:radio_sposob>Department</tns:radio_sposob>
                                </tns:Panel_Get_result>
                            </tns:Request>
                        </MessagePrimaryContent>
                        <RefAttachmentHeaderList>
                            <RefAttachmentHeader>
                                <uuid>1b0d3a3a-0616-403f-946b-1c14ac384239</uuid>
                                <Hash>3RNKfXjGXT4NQrjmmm7b6CEOrS044njPPq2U7HQ+EGE=</Hash>
                                <MimeType>application/zip</MimeType>
                                <SignaturePKCS7>
                                    <xop:Include xmlns:xop="http://www.w3.org/2004/08/xop/include" href="cid:d0abc6a3-f82c-46fa-a2cf-6b1b8b78c460-652793@urn%3A%2F%2Fx-artefacts-smev-gov-ru%2Fservices%2Fmessage-exchange%2Ftypes%2Fbasic%2F1.1"/>
                                </SignaturePKCS7>
                            </RefAttachmentHeader>
                        </RefAttachmentHeaderList>
                    </ns2:SenderProvidedRequestData>
                    <ns2:MessageMetadata>
                        <ns2:MessageId>047b500c-04a4-11eb-af32-fa163eff7bf8</ns2:MessageId>
                        <ns2:MessageType>REQUEST</ns2:MessageType>
                        <ns2:Sender>
                            <ns2:Mnemonic>MNSV05</ns2:Mnemonic>
                            <ns2:HumanReadableName>ЕПГУ (svcdev)</ns2:HumanReadableName>
                        </ns2:Sender>
                        <ns2:SendingTimestamp>2020-10-02T14:40:08.000+03:00</ns2:SendingTimestamp>
                        <ns2:DestinationName>unknown</ns2:DestinationName>
                        <ns2:Recipient>
                            <ns2:Mnemonic>03UD02</ns2:Mnemonic>
                            <ns2:HumanReadableName>ГИС ОГД</ns2:HumanReadableName>
                        </ns2:Recipient>
                        <ns2:SupplementaryData>
                            <ns2:DetectedContentTypeName>not detected</ns2:DetectedContentTypeName>
                            <ns2:InteractionType>NotDetected</ns2:InteractionType>
                        </ns2:SupplementaryData>
                        <ns2:DeliveryTimestamp>2020-10-06T12:51:26.416+03:00</ns2:DeliveryTimestamp>
                        <ns2:Status>responseIsDelivered</ns2:Status>
                    </ns2:MessageMetadata>
                    <FSAttachmentsList>
                        <FSAttachment>
                            <uuid>1b0d3a3a-0616-403f-946b-1c14ac384239</uuid>
                            <UserName>3MSVWESNTfOjxYCyl1W4cuWbmMeCs9</UserName>
                            <Password>Y3oxXKp4PuStEFPWjgwL1qyX6rmGXE</Password>
                            <FileName>/SignedContent.zip</FileName>
                        </FSAttachment>
                    </FSAttachmentsList>
                    <ns2:ReplyTo>eyJzaWQiOjMxNzE0LCJtaWQiOiIwNDdiNTAwYy0wNGE0LTExZWItYWYzMi1mYTE2M2VmZjdiZjgiLCJ0Y2QiOiJiMTJkNTJlNi0wNGEzLTExZWItOGI4Ni1mYTE2M2VlNGI4NDkiLCJlb2wiOjAsInNsYyI6Imdpc29nZDczX2dwenVfMS4wLjBfUmVxdWVzdCIsIm1ubSI6Ik1OU1YwNSJ9</ns2:ReplyTo>
                </ns2:Request>
                <ns2:SMEVSignature>
                    <ds:Signature xmlns:ds="http://www.w3.org/2000/09/xmldsig#">
                        <ds:SignedInfo>
                            <ds:CanonicalizationMethod Algorithm="http://www.w3.org/2001/10/xml-exc-c14n#"/>
                            <ds:SignatureMethod Algorithm="urn:ietf:params:xml:ns:cpxmlsec:algorithms:gostr34102012-gostr34112012-256"/>
                            <ds:Reference URI="#SIGNED_BY_SMEV">
                                <ds:Transforms>
                                    <ds:Transform Algorithm="http://www.w3.org/2001/10/xml-exc-c14n#"/>
                                    <ds:Transform Algorithm="urn://smev-gov-ru/xmldsig/transform"/>
                                </ds:Transforms>
                                <ds:DigestMethod Algorithm="urn:ietf:params:xml:ns:cpxmlsec:algorithms:gostr34112012-256"/>
                                <ds:DigestValue>dBqVs+Alv+Lwhuj6+7h/eQzouPT64VHgjOVT5n3b30Y=</ds:DigestValue>
                            </ds:Reference>
                        </ds:SignedInfo>
                        <ds:SignatureValue>jEDI/eO947HjY4KRYdFrvlevJ/pG/d9DYfefFHNhRKrU5HMZaEh2WsntDLD73si3UUbI07WgqsVZ/eKSM/ttkQ==</ds:SignatureValue>
                        <ds:KeyInfo>
                            <ds:X509Data>
                                <ds:X509Certificate>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</ds:X509Certificate>
                            </ds:X509Data>
                        </ds:KeyInfo>
                    </ds:Signature>
                </ns2:SMEVSignature>
            </ns2:RequestMessage>
        </ns2:GetRequestResponse>
    </soap:Body>
</soap:Envelope>
```

#### 2.1: get Attachment if it pinned

##### 2.1.a FTP Attachment

- given xml

```xml
<FSAttachmentsList>
  <FSAttachment>
    <uuid>1b0d3a3a-0616-403f-946b-1c14ac384239</uuid>
    <UserName>3MSVWESNTfOjxYCyl1W4cuWbmMeCs9</UserName>
    <Password>Y3oxXKp4PuStEFPWjgwL1qyX6rmGXE</Password>
    <FileName>/SignedContent.zip</FileName>
  </FSAttachment>
</FSAttachmentsList>
```

- POST `localhost:8080/v1/file/from_smev`
  *download file from smev ftp*

```json
->
{
    "user": "3MSVWESNTfOjxYCyl1W4cuWbmMeCs9",
    "password": "Y3oxXKp4PuStEFPWjgwL1qyX6rmGXE",
    "path": "/SignedContent.zip"
}
```

```json
<-
{
    "job": "81aaa162-4c5a-49b4-bbbc-bd8763faeb79"
}
```

- GET `localhost:8080/v1/file/from_smev/81aaa162-4c5a-49b4-bbbc-bd8763faeb79`
  *get job status*

```json
<-
{
    "id": "a43670751a4f405d8e16ef6a8c5598296d3ee66f",
    "path": "/app/storage/2020-10-06/a43670751a4f405d8e16ef6a8c5598296d3ee66f.SignedContent.zip"
}
```

- GET `localhost:8080/v1/file/a43670751a4f405d8e16ef6a8c5598296d3ee66f`

```
<-
return a file
```

##### 2.1.b MTOM Attachment

- given xml

```xml
<AttachmentsContentList>
  <AttachmentsContent>
    <Id>1b0d3a3a-0616-403f-946b-1c14ac384239</Id>
    <Content>BASE64 String of file</Content>
  </AttachmentsContent>
</AttachmentsContentList>
```
*`Content` is base64 string of file*

#### 3: ack a request

- POST `localhost:8080/v1/plugin/finish_response`

```json
->
{
    "id": "047b500c-04a4-11eb-af32-fa163eff7bf8",
    "cert_type": "ulyanovsk",
    "smev_host": "smev-test-1-1"
}
```

```json
<-
{
    "id": "047b500c-04a4-11eb-af32-fa163eff7bf8",
}
```

- *After that, the message chain will be marked as taken for work and will no longer be shown at ` localhost:8080/v1/records/worker`*

#### 4: Send a response

- POST `localhost:8080/v1/plugin/reply`

```json
->
{
    "smev_host": "smev-test-1-1",
    "id": "95f13cba-07d7-11eb-b28a-37ea2fa18a4c",
    "message": {
        "xsd_type": "Response",
        "json_template": {
            "foo": "bar"
        },
        "cert_type": "ulyanovsk"
    },
    "attachment": {
        "files": [
            {
                "url": "http://95.68.241.62/files.md5/1a/3b/07865a6c379fc1304415dcc58f703b1a",
                "name": "file.xml"
            }
        ],
        "cert_type": "ulyanovsk"
    }
}
```

```json
<-
{
    "id": "95f13cba-07d7-11eb-b28a-37ea2fa18a4c"
}
```