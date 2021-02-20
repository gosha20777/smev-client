# Plugins: Rosreestr

### Общие положения

1. запрос имеет следующую структуру

- XML конверт с сообщением
- ZIP архив с XML и SIG файлами:
  - app_1.xml - шаблон с запросом (документ заявления `$document`)
  - request.xml - описание формы заявления (`$request`)

2. Структура zip архива не меняется и остается одинаковой.
3. Шаблон файлов  `app_1.xml`  и `request.xml` не меняется и остается одинаковым

## Файлы

- `message-teamplate.xml`

```xml
<req:Request xmlns:das="urn://x-artefacts-rosreestr-gov-ru/virtual-services/egrn-statement/dRegionsRF/1.0.0"
			 xmlns:req="urn://x-artefacts-rosreestr-gov-ru/virtual-services/egrn-statement/1.1.2"
			 xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
<!-- @PARAM region_code -->
    <req:region>50</req:region>
<!-- @PARAM external_number -->
	<req:externalNumber>did запроса</req:externalNumber>
<!-- @PARAM sender_type -->
	<req:senderType>Vedomstvo</req:senderType>
<!-- @PARAM action_code -->
	<req:actionCode>659511111112</req:actionCode>
	<req:Attachment>
		<req:IsMTOMAttachmentContent>true</req:IsMTOMAttachmentContent>
		<req:RequestDescription>
			<req:IsUnstructuredFormat>false</req:IsUnstructuredFormat>
			<req:IsZippedPacket>true</req:IsZippedPacket>
			<req:fileName>request.xml</req:fileName>
		</req:RequestDescription>
		<req:Statement>
			<req:IsUnstructuredFormat>false</req:IsUnstructuredFormat>
			<req:IsZippedPacket>true</req:IsZippedPacket>
			<req:fileName>app_1.xml</req:fileName>
		</req:Statement>
		<req:File>
			<req:IsUnstructuredFormat>true</req:IsUnstructuredFormat>
			<req:IsZippedPacket>true</req:IsZippedPacket>
			<req:fileName>app_1.xml.sig</req:fileName>
		</req:File>
		<req:File>
			<req:IsUnstructuredFormat>true</req:IsUnstructuredFormat>
			<req:IsZippedPacket>true</req:IsZippedPacket>
			<req:fileName>request.xml.sig</req:fileName>
		</req:File>
	</req:Attachment>
</req:Request>
```

- `request.zip/request.xml`

```xml
<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<request xmlns="http://rosreestr.ru/services/v0.12/TRequest">
    <statementFile>
        <fileName>app_1.xml</fileName>
    </statementFile>
    <file>
        <fileName>request.xml</fileName>
    </file>
<!-- @PARAM request.type -->
    <requestType>111300003000</requestType>
</request>
```

- `request.zip/app_1.xml`

```xml
<?xml version="1.0" encoding="UTF-8"?>
<tns:EGRNRequest xmlns:dHouse="http://rosreestr.ru/services/v0.1/commons/directories/house" 
... >
	<!-- Заголовок запроса на предоставление сведений из ЕГРН -->
	<tns:header>
		<!-- Предоставление сведений, содержащихся в ЕГРН, об объектах недвижимости и (или) их правообладателях-->
<!--    @PARAM action_code -->
		<stCom:actionCode>659511111112</stCom:actionCode>
		<!-- Запрос на предоставление сведений, содержащихся в ЕГРН, об объектах недвижимости и (или) их правообладателях-->
<!--    @PARAM document.statement_type -->
		<stCom:statementType>558630200000</stCom:statementType>
<!--    @PARAM document.creation_date = datatime.now() -->
		<stCom:creationDate>2020-04-30T18:13:51.0</stCom:creationDate>
	</tns:header>
	<tns:declarant _id="2">
		<subj:other>
<!--    	@PARAM document.organiation.name -->
			<subj:name>Комитет по архитектуре и градостроительству Московской области
</subj:name>
<!--    	@PARAM document.organization.inn -->
			<subj:inn>7707018904</subj:inn>
<!--    	@PARAM document.organization.ogrn -->
			<subj:ogrn>1027700546510</subj:ogrn>
<!--    	@PARAM document.organization.kpp -->
			<subj:kpp>502401001</subj:kpp>
<!--    	@PARAM document.organization.registration_date -->
			<subj:regDate>2000-08-24</subj:regDate>
		</subj:other>
		<!-- Органы государственной власти субъектов Российской Федерации-->
<!--    @PARAM document.organiation_type -->
		<subj:declarantKind>357013000000</subj:declarantKind>
	</tns:declarant>
	<tns:requestDetails>
		<tns:requestEGRNDataAction>
			<tns:extractDataAction>
				<tns:object>
					<!-- 002001001000	Земельный участок-->
<!--    			@PARAM document.action.object_type_code -->
					<obj:objectTypeCode>002001001000</obj:objectTypeCode>
					<obj:cadastralNumber>
<!--    				@PARAM document.action.cadastral_number -->
						<obj:cadastralNumber>50:30:0060204:1</obj:cadastralNumber>
					</obj:cadastralNumber>
				</tns:object>
				<!-- extractRealty	Выписка из Единого государственного реестра объектов недвижимости об объекте недвижимости
extractRealtyList	Выписка из Единого государственного реестра объектов недвижимости о переходе прав на объект недвижимости
extractEquityConstructionContract	Выписка из Единого государственного реестра объектов недвижимости о зарегистрированных договорах участия в долевом строительстве
extractObjectMainFeaturesRights	Выписка из Единого государственного реестра объектов недвижимости об основных характеристиках и зарегистрированных правах на объект недвижимости
extractStatementReceiptDate	Выписка о дате получения органом регистрации прав заявления о государственном кадастровом учете и (или) государственной регистрации прав и прилагаемых к нему документов
-->
<!--    		@PARAM document.request_type -->
				<tns:requestType>extractRealty</tns:requestType>
			</tns:extractDataAction>
		</tns:requestEGRNDataAction>
	</tns:requestDetails>
	<tns:deliveryDetails>
		<stCom:resultDeliveryMethod>
<!--    		@PARAM document.result_type -->
			<stCom:recieveResultTypeCode>webService</stCom:recieveResultTypeCode>
		</stCom:resultDeliveryMethod>
	</tns:deliveryDetails>
	<tns:statementAgreements>
<!--    		@PARAM document.processing_agreement -->
		<stCom:persDataProcessingAgreement>01</stCom:persDataProcessingAgreement>
<!--    		@PARAM document.data_agreement -->
		<stCom:actualDataAgreement>01</stCom:actualDataAgreement>
	</tns:statementAgreements>
</tns:EGRNRequest>
```

### Модель данных



```python
class Organization(BaseModel):
    name: str
    inn: str
    ogrn: str
    registration_date: str
    type_org: int

class Action(BaseModel):
    object_type_code: int
    cadastral_number: str

class Document(BaseModel):
    statement_type: int = 558630200000
    creation_date: str = str(datetime.now())
    request_type: str = 'extractRealty'
    processing_agreement: str = '01'
    data_agreement: str = '01'
    organization: Organization
    action: Action

class SmevMesageRosReestrRequest(BaseModel):
    message_sert: str
    attachment_sert: str
    smev_host: str
    region_code: int
    external_number: str = '832dc687-a2aa-4a3d-98fb-922e73e6a9e4'
    sender_type: str = 'Vedomstvo'
    action_code: int = 659511111112
    request_type: int = 111300003000
    document: Document
```



```json
{
    "message_sert": str,
    "attachment_sert": str,
    "smev_host": str,
    "region_code": int,
    "external_number": str (832dc687-a2aa-4a3d-98fb-922e73e6a9e4),
	"sender_type": str (Vedomstvo),
    "action_code": int (659511111112),
    "request_type": int (111300003000),
    "document": {
        "statement_type": int (558630200000),
        "creation_date": str (datetime.now()),
        "request_type": str (extractRealty),
        "processing_agreement": str (01),
        "data_agreement": str (01),
        "organization": {
            "name": str,
    		"inn": str,
    		"ogrn": str,
    		"registration_date": str,
    		"type_org": int
        },
        action: {
            "object_type_code": int,
            "cadastral_number": str
        }
    }
}
```

## API

- POST `/v1/plugin/send_request_ros_reestr`

```
->
Json imput model
<-
{
	"id": record uuid
}
```

- GET `/v1/record/{id}`

```
{
	"id" id,
	"date": date,
	"mesages": [ messages array ]
}
```

- GET `/v1/record/{id}/{message_type}` - to get current message
- GET `/v1/record/{id}/{message_type}/xml` - to get raw xml content

- POST `/v1/plugin/finish_request` - to ack and clear record

```
->
{
	"id": record id,
	"cert_type": cert type (same as request's message_sert),
	"smev_host": smev host (same as request's smev_host)
}
<-
{
	"id": record id
}
```

