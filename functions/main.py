import logging

from flask import jsonify
from flask import make_response

from openapi_server import connexion_app


def receive_http_store_blob_trigger_func(req):
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
        response = make_response(jsonify(problem), 415)
        response.headers['Content-Type'] = 'application/problem+json',
        return response

    try:
        req_body = req.get_json(silent=True)
    except ValueError:
        problem = {'type': 'InvalidJSON',
                   'title': 'Invalid JSON',
                   'status': 400}
        response = make_response(jsonify(problem), 415)
        response.headers['Content-Type'] = 'application/problem+json',
        return response

    result = connexion_app.handle_request(url='/generic', method=req.method, headers=req.headers,
                                          data=req_body)

    return make_response(jsonify(result.data), result.status_code)
