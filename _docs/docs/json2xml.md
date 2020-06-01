# Smev-3 client: json2xml

*Service location:* `./json2xml-transformer`

*Service purpose:* json to xml conversion according to xsd schemes

*config files:* 

- `./json2xml-transformer/XSD-SMEV-NUMBER/*.xsd` - smev3 mesage type's xsd chemes
- `./json2xml-transformer/log-config.yaml` - logging config

## API

- **POST** `/api/v1/{xsd_element}`
  *request*

  ```json
  {
      xsd_params: json
  }
  ```

  *response*

  ```json
  {
      "xml": str
  }
  ```

  *where*

  - `xsd_element` - name of xsd element
  - `xsd_params` - json object which configure xsd content or xsd choice
  - `xml` - result xml mesage

## Configuration

Put your xsd files and common folders at `xsd` directory and restart the app. Application will recursive load it.

## Usage examples

### Example 1

*template of given xsd (full xsd path: `xsd/34087/fns-vipul-tosmv-ru.xsd`).*

```xml
<?xml version="1.0" encoding="UTF-8"?>
<xs:schema .../>
	<xs:element name="FNSVipULRequest">
		<xs:complexType>
			<xs:sequence>
				<xs:element name="ЗапросЮЛ">
					<xs:complexType>
						<xs:choice>
							<xs:element name="ОГРН" type="fnst:OGRNCompanyType"/>
							<xs:element name="ИННЮЛ" type="fnst:LegalPersonINNType"/>
						</xs:choice>
					</xs:complexType>
				</xs:element>
			</xs:sequence>
			<xs:attribute name="ИдДок" type="fnst:string-36" use="required"/>
			<xs:attribute name="НомерДела" type="fnst:string-50" use="optional"/>
		</xs:complexType>
	</xs:element>
      ...
</xs:schema>
```

*request*

```json
POST localhost:5000/api/v1/FNSVipULRequest/
Request:
{
	"ЗапросЮЛ": {
		"ОГРН": "1027700070518"
	},
	"ИдДок": "3"
}

Response:
{	"xml": "<ns0:FNSVipULRequest xmlns:ns0=\"urn://x-artefacts-fns-vipul-tosmv-ru/311-14/4.0.6\" ИдДок=\"3\"><ns0:ЗапросЮЛ><ns0:ОГРН>1027700070518</ns0:ОГРН></ns0:ЗапросЮЛ></ns0:FNSVipULRequest>"
}
```

*result*

```xml
<ns0:FNSVipULRequest
     				 xmlns:ns0="urn://x-artefacts-fns-vipul-tosmv-ru/311-14/4.0.6"
                     ИдДок="3">
    <ns0:ЗапросЮЛ>
        <ns0:ОГРН>1027700070518</ns0:ОГРН>
    </ns0:ЗапросЮЛ>
</ns0:FNSVipULRequest>
```

### Example 2

*full xsd path: `xsd/167116/....xsd`).*

*request*

```json
POST localhost:5000/api/v1/PublicPrintOutRequest/
Request:
{
	"ExpertiseResultNumber": "00-1-2-3-000010-2000",
	"ExpertiseResultDate": "2017-12-01"
}

Response:
{
    "xml": "<ns0:PublicPrintOutRequest xmlns:ns0=\"urn://x-artefacts-gis-ergz-public/2.0.0\"><ns1:ExpertiseResultNumber xmlns:ns1=\"urn://x-artefacts-gis-ergz-types/2.0.0\">00-1-2-3-000010-2000</ns1:ExpertiseResultNumber><ns2:ExpertiseResultDate xmlns:ns2=\"urn://x-artefacts-gis-ergz-types/2.0.0\">2017-12-01</ns2:ExpertiseResultDate></ns0:PublicPrintOutRequest>"
}
```

*result*

```xml
<ns0:PublicPrintOutRequest xmlns:ns0="urn://x-artefacts-gis-ergz-public/2.0.0" xmlns:egrzt="urn://x-artefacts-gis-ergz-types/2.0.0">
	<ns1:ExpertiseResultNumber xmlns:ns1="urn://x-artefacts-gis-ergz-types/2.0.0">00-1-2-3-000010-2000</ns1:ExpertiseResultNumber>
    <ns2:ExpertiseResultDate xmlns:ns2="urn://x-artefacts-gis-ergz-types/2.0.0">2017-12-01</ns2:ExpertiseResultDate>
</ns0:PublicPrintOutRequest>
```

### Example 3

*full xsd path: `xsd/168866/....xsd`).*

*request*

```json
POST localhost:5000/api/v1/FullPrintOutRequest/
Request 1:
{
	"ExpertiseResultNumber": "00-1-2-3-000010-2000",
	"ExpertiseResultDate": "2017-12-01"
}

Response 1:
{
    "xml": "<ns0:FullPrintOutRequest xmlns:ns0=\"urn://x-artefacts-gis-ergz/2.0.0\"><ns1:ExpertiseResultNumber xmlns:ns1=\"urn://x-artefacts-gis-ergz-types/2.0.0\">00-1-2-3-000010-2000</ns1:ExpertiseResultNumber><ns2:ExpertiseResultDate xmlns:ns2=\"urn://x-artefacts-gis-ergz-types/2.0.0\">2017-12-01</ns2:ExpertiseResultDate></ns0:FullPrintOutRequest>"
}
```

### Example 4

*full xsd path: `xsd/169092/....xsd`).*

*request*

```json
POST localhost:5000/api/v1/DocumentsProlongationRequest/
Request 1:
{
	"PrintOutNumber": "00000000-0000-0000-0000-000000000001",
	"Operation": {
		"Prolongation": {
			"ProlongationPeriod": 10
		}
	}
}

Response 1:
{
    "xml": "<ns0:DocumentsProlongationRequest xmlns:ns0=\"urn://x-artefacts-gis-ergz-documents-prolongation/2.0.0\"><ns1:PrintOutNumber xmlns:ns1=\"urn://x-artefacts-gis-ergz-types/2.0.0\">00000000-0000-0000-0000-000000000001</ns1:PrintOutNumber><ns0:Operation><ns0:Prolongation><ns0:ProlongationPeriod>10</ns0:ProlongationPeriod></ns0:Prolongation></ns0:Operation></ns0:DocumentsProlongationRequest>"
}
```