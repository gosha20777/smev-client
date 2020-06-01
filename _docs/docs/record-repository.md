# Smev-3 client: record-repository

*Service location:* `./record-repository`

*Service purpose:* manipulating and storing smev message series

*config files:* 

- `./record-repository/app.inc` - system variables for connection to Postgres database

## API

- **GET** `/api/v1/record/new?id=id`

  *response*

  ```json
  {
      "id": string,
      "mesages": [],
      "date": date
  }
  ```

  *where:*

  - query param `id` - uuid, default value is random UUID4
  - `id` - uuid
  - `mesages` - array of existing in mesage mesage types e.g. `[ "GetResponseRequest", "GetResponseResponse", "AckRequest" ]`

- **GET** `/api/v1/record/{id}`

  *response*

  ```json
  {
      "id": string,
      "mesages": [],
      "date": string-date
  }
  ```

- **GET** `/api/v1/record/{id}/{mesage_type}`

  *response*

  ```json
  {
      "id": string,
      "xml": string
  }
  ```
  *where:*

  - `mesage_type` - type of mesage in record e.g. AckRequest
  
- **GET** `/api/v1/record/{id}/{mesage_type}/xml`

  *response*

  ```xml
  rew xml message
  ```
  
- **PUT** `/api/v1/record/{id}/{mesage_type}`

  *request*

  ```json
  {
      "xml": string
  }
  ```
  *response*

   ```json
  {
      "updated_records": number
  }
   ```
  *where:*

  - `updated_records` - number of updated records

- **PUT** `/api/v1/record/{id}/{mesage_type}/xml`

  *request*

  ```xml
  raw xml
  ```
  *response*
  
   ```json
  {
      "updated_records": number
  }
   ```
  
- **DALATE** `/api/v1/record/{id}`

  *response*
  
   ```json
  {
      "remove_records": number
  }
   ```
  *where:*
  
  - `remove_records` - number of removed records
