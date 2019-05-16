import logging

import requests
import config
import json

from flask import jsonify
from flask import make_response
from requests_oauthlib import OAuth1

from openapi_server import connexion_app
from surveys.csv import handle_csv
from surveys.csv.helpers import get_presentable_surveys


def handle_http_store_blob_trigger_func(request):
    logging.basicConfig(level=logging.info)
    logging.info('Python HTTP handle_http_store_blob_trigger_func function processed a request from %s.', request.path)

    logging.info(request.headers)
    logging.info(request.args)

    if not request.args or 'geturl' not in request.args or request.args['geturl'] not in config.URL_COLLECTIONS:
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

    request_def = config.URL_COLLECTIONS[request.args['geturl']]
    logging.info('Strored definition {}'.format(request_def))

    if request_def['method'] == 'GET':
        return get_http_store_blob_trigger_func(request)
    elif request_def['method'] == 'POST':
        media_type = request_def['body']['type']
        data = request_def['body']['content']
        cpHeaders = request_def['headers']
        cpHeaders['Content-Type'] = media_type

        moreapp_config = request_def['authorization']['type'] == 'MoreApp'
        if 'authorization' in request_def and not moreapp_config:
            cpHeaders['Authorization'] = request_def['authorization']['type'] + ' '\
                                         + request_def['authorization']['credentials']

        logging.info(cpHeaders)
        logging.info(request_def['url'])
        logging.info(data)

        if moreapp_config:
            oauth_1 = OAuth1(
                config.CONSUMER_KEY,
                config.CONSUMER_SECRET,
                signature_method='HMAC-SHA1'
            )

            data_response = requests.post(
                request_def['url'],
                auth=oauth_1,
                data=json.dumps(data),
                json=json.dumps(data),
                headers=cpHeaders
            )
        else:
            data_response = requests.post(
                request_def['url'],
                data=json.dumps(data),
                headers=cpHeaders,
            )

        if data_response.status_code != requests.codes.ok:
            logging.error(data_response.headers)
            logging.error(data_response.status_code)
            logging.error(data_response.text)
            problem = {'type': 'DataError',
                       'title': 'Error requesting data',
                       'content': json.dumps(data_response.json()),
                       'status': 400}
            response = make_response(jsonify(problem), 400)
            response.headers['Content-Type'] = 'application/problem+json',
            return response

        return connexion_app.handle_request(
            url=request.args['storepath'],
            method='POST',
            headers={'Content-Type': 'application/json'},
            data=get_presentable_surveys(data_response.json()['elements']) if moreapp_config else data_response.json()
            )
    else:
        problem = {'type': 'InvalidRequest',
                   'title': 'Invalid Request',
                   'status': 400}
        response = make_response(jsonify(problem), 415)
        response.headers['Content-Type'] = 'application/problem+json',
        return response


def receive_http_store_blob_trigger_func(request):
    logging.basicConfig(level=logging.info)
    logging.info('Python HTTP receive_http_store_blob_trigger_func function processed a request from %s.', request.path)

    logging.debug(request.headers)

    req_body = None

    if request.method == "POST":
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

    if not request.args or 'geturl' not in request.args or request.args['geturl'] not in config.URL_COLLECTIONS:
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
        data = requests.get(config.URL_COLLECTIONS[request.args['geturl']]['url']).json()
    except requests.exceptions.ConnectionError:
        logging.warning('Error retrieving data from [%s]', config.URL_COLLECTIONS[request.args['geturl']]['url'])
        problem = {'type': 'InternalConfigError',
                   'title': 'Internal configuration incorrect',
                   'status': 500}
        response = make_response(jsonify(problem), 500)
        response.headers['Content-Type'] = 'application/problem+json',
        return response

    return connexion_app.handle_request(url=request.args['storepath'], method='POST',
                                        headers={'Content-Type': 'application/json'}, data=data)


def get_csv_survey_blob_func():
    """
    This aims to create a csv file from all
    the registrations that have been downloaded
    """

    bucket = config.GOOGLE_STORAGE_BUCKET
    return handle_csv.create_survey_csv(bucket)
