import logging
import requests
import config

from flask import jsonify
from flask import make_response

from openapi_server import connexion_app


def receive_http_store_blob_trigger_func(request):
    logging.basicConfig(level=logging.info)
    logging.info('Python HTTP receive_http_store_blob_trigger_func function processed a request from %s.', request.path)

    logging.info(request.headers)

    media_type = ""

    try:
        media_type = request.headers['Content-Type']
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
        req_body = request.get_json(silent=True)
    except ValueError:
        problem = {'type': 'InvalidJSON',
                   'title': 'Invalid JSON',
                   'status': 400}
        response = make_response(jsonify(problem), 415)
        response.headers['Content-Type'] = 'application/problem+json',
        return response

    cpHeaders = {}

    for key, value in request.headers:
        cpHeaders[key] = value

    return connexion_app.handle_request(url=request.path, method=request.method, headers=cpHeaders,
                                        data=req_body)


def get_http_store_blob_trigger_func(request):
    logging.basicConfig(level=logging.info)
    logging.info('Python HTTP get_http_store_blob_trigger_func function processed a request')

    if not request.args or 'geturl' not in request.args or request.args['geturl'] not in config.GET_URLS:
        problem = {'type': 'MissingParameter',
                   'title': 'Expected parameter geturl not found',
                   'status': 400}
        response = make_response(jsonify(problem), 400)
        response.headers['Content-Type'] = 'application/problem+json',
        return response

    if not request.args or 'storepath' not in request.args:
        problem = {'type': 'MissingParameter',
                   'title': 'Expected parameter storepath not found',
                   'status': 400}
        response = make_response(jsonify(problem), 400)
        response.headers['Content-Type'] = 'application/problem+json',
        return response

    try:
        data = requests.get(config.GET_URLS[request.args['geturl']]).json()
    except requests.exceptions.ConnectionError:
        logging.warning('Error retrieving data from [%s]', config.GET_URLS[request.args['geturl']])
        problem = {'type': 'InternalConfigError',
                   'title': 'Internal configuration incorrect',
                   'status': 500}
        response = make_response(jsonify(problem), 500)
        response.headers['Content-Type'] = 'application/problem+json',
        return response

    return connexion_app.handle_request(url=request.args['storepath'], method='POST',
                                          headers={'Content-Type': 'application/json'}, data=data)
