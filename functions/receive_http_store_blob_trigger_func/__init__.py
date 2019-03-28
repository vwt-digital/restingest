import logging
import json

import azure.functions as func

from receive_http_store_blob_trigger_func.openapi_server import connexion_app


def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.basicConfig(level=logging.info)
    logging.info('Python HTTP trigger function processed a request.')

    logging.info(req.headers)

    media_type = ""

    try:
        media_type = req.headers['Content-Type']
    except KeyError:
        pass

    if not media_type or media_type != 'application/json':
        problem = {'type': 'InvalidMediaType',
                   'title': 'Unsupported media type, expected application/json',
                   'status': 415}
        return func.HttpResponse(json.dumps(problem),
                                 mimetype="application/problem+json",
                                 status_code=415)

    try:
        req_body = req.get_json()
    except ValueError:
        problem = {'type': 'InvalidJSON',
                   'title': 'Invalid JSON',
                   'status': 400}
        return func.HttpResponse(json.dumps(problem),
                                 mimetype="application/problem+json",
                                 status_code=problem['status'])

    result = connexion_app.handle_request(url=req.url, method=req.method, headers=req.headers, data=json.dumps(req_body))

    return func.HttpResponse(result.data, status_code=result.status_code)
