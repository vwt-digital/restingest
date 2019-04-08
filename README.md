# restingest
REST API to ingest into cloud storage

Restingest provides an HTTP endpoint to which JSON documents can be posted to be stored in blob storage.
The [config.py](functions/config.py) file (see [config.example.py](functions/config.example.py) for an example) defines where the blobs will be stored, by specifying the AZURE_XXX and/or GOOGLE_XXX entries. The blobs will be stored in a path starting with BASE_PATH as configured in config.py, followed by year/month/day. The filename will be a timestamp in UTC, e.g. ```base/path/2019/04/08/20190408T135601.json```

By default, any JSON document will be accepted. It is possible to constraint the JSON that will be accepted by specifying a custom OpenAPI specification. See below for more information.

## Running
Running restingest can be done by one of the following three ways.

### 1. Using Flask
#### Run as a local Flask app
~~~
cd functions
export FLASK_APP=openapi_server:app
flask run
~~~
#### Using the Flask app endpoint
The Flask app will service and endpoint to which a JSON body can be posted, which will then be stored in the cloud storage. When using the default OpenAPI specificition, any JSON will be accepted at the /generic path. For example:
~~~
curl -X POST -H "Content-Type: application/json" \
  -d '{"some_data":"abc","some_more_data":"abc"}' \
  http://localhost:5000/generic
~~~

### 2. Cloud Functions POST endpoint
#### On google
~~~
cd functions
gcloud functions deploy post-func --entry-point=receive_http_store_blob_trigger_func \
  --runtime=python37 --trigger-http
~~~

#### On Azure (not working)
~~~
cd functions
func azure functionapp publish restingest-funca
~~~

#### Usage of POST endpoint
This will deploy function endpoints to which a JSON body can be posted, which will then be stored in the cloud storage. When using the default OpenAPI specificition, any JSON will be accepted at the /generic path. For example:
~~~
curl -X POST -H "Content-Type: application/json" \
  -d '{"some_data":"abc","some_more_data":"abc"}' \
  https://functionendpoint.example.com/generic
~~~

### 3. Cloud Functions GET timer
#### On Google
~~~
cd functions
gcloud functions deploy post-func --entry-point=get_http_store_blob_trigger_func \
  --runtime=python37 --trigger-http
gcloud beta scheduler jobs create http geturl1-job --schedule="*/5 * * * *" \
   --uri=https://functionendpoint.example.com?geturl=url1&storepath=url1result
~~~

#### On Azure (not working)
See above

#### Usage of GET timer
The GET timer will get the data from the geturl specified in the correspinding entry of GET_URLS in [config.py](functions/config.py) and store it in a blob on the path `<BASE_PATH>/<storepath>/yyyy/mm/dd/yyyymmddThhiiss.json`.

## Using a custom OpenAPI server
A more restrictive format of the JSON documents can be applied by overwriting the default [openapi.yaml](functions/openapi_server/openapi/openapi.yaml). All endpoints should be handled by the _generic_post_ handler.
For example, to store pet documents from the [OpenAPI petstore example](https://github.com/OAI/OpenAPI-Specification/blob/master/examples/v3.0/petstore.yaml), use the below specification. This will only accept POSTs with a JSON body containing an id field and name field in the correct format, as specified in the OpenAPI specification.
~~~
openapi: "3.0.0"
info:
  version: 1.0.0
  title: Swagger Petstore
  license:
    name: MIT
paths:
  /pets:
   post:
      summary: Create a pet
      operationId: generic_post
      tags:
        - pets
      requestBody:
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/Pet'
      responses:
        '201':
          description: Null response
components:
  schemas:
    Pet:
      required:
        - id
        - name
      properties:
        id:
          type: integer
          format: int64
        name:
          type: string
        tag:
          type: string
~~~
