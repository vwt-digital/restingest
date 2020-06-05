import logging
import os
import base64

import requests
import config
import json

from xml.etree import ElementTree
from google.cloud import kms_v1

from flask import jsonify
from flask import make_response
from requests_oauthlib import OAuth1

from openapi_server import connexion_app
from xml.sax.saxutils import escape


def get_authentication_secret():
    authentication_secret_encrypted = base64.b64decode(os.environ['AUTHENTICATION_SECRET_ENCRYPTED'])
    kms_client = kms_v1.KeyManagementServiceClient()
    crypto_key_name = kms_client.crypto_key_path_path(os.environ['PROJECT_ID'], os.environ['KMS_REGION'], os.environ['KMS_KEYRING'],
                                                      os.environ['KMS_KEY'])
    decrypt_response = kms_client.decrypt(crypto_key_name, authentication_secret_encrypted)
    return decrypt_response.plaintext.decode("utf-8").replace('\n', '')


def gather_authorization_headers(request_def):
    authorization_headers = {}

    if 'authorization' in request_def:
        authorization_def = request_def['authorization']
        authorization_type = authorization_def.get('type', '')

        if authorization_type == 'OAuth1':
            # no authorization headers required
            authorization_headers = {}
        elif authorization_type == 'CustomHeaderAPIKey':
            if 'credentials' in authorization_def:
                credentials = authorization_def['credentials']
            else:
                credentials = get_authentication_secret()
            authorization_headers[authorization_def['custom_header_name']] = credentials
        elif authorization_type:
            if 'credentials' in authorization_def:
                credentials = authorization_def['credentials']
            else:
                credentials = get_authentication_secret()
            authorization_headers['Authorization'] = authorization_type + ' ' + credentials

    return authorization_headers


def http_request_store_blob_trigger_func(request):
    logging.basicConfig(level=logging.info)
    logging.info('Python HTTP handle_http_store_blob_trigger_func function processed a request from %s.', request.path)

    if not request.args or 'geturl' not in request.args or request.args['geturl'] not in config.URL_COLLECTIONS:
        problem = {'type': 'MissingParameter',
                   'title': 'Expected parameter geturl not found or invalid',
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
    logging.info('Stored definition {}'.format(request_def))

    skip = None
    taken = 0
    take_size = request_def.get('pagination', {}).get('take_size', 0)
    while not skip or taken == take_size:
        result_response, data_response = request_store_blob_trigger(request.args['storepath'], request_def, skip)

        if take_size:
            taken = count_elements(request_def, data_response)

            if taken:
                skip = (skip if skip else 0) + taken
            else:
                break
        else:
            break

    return result_response


def count_elements(request_def, data_response):
    taken = None
    content_type = data_response.headers.get('Content-Type', None)

    if content_type.startswith('application/json'):
        json_body = data_response.json()

        if 'count_element' in request_def['pagination']:
            taken = len(json_body[request_def['pagination']['count_element']])
        else:
            taken = len(json_body)
    elif content_type.startswith('application/xml') or content_type.startswith('text/xml') or \
            content_type.startswith('application/atom+xml'):
        xml_body = ElementTree.XML(data_response.content)
        count_element = request_def['pagination'].get('count_element', '*')
        taken = len(xml_body.findall(f'{count_element}'))
    else:
        logging.warning(f"Pagination specified but only supported for application/json response, not for "
                        f"{data_response.headers['Content-Type']}")

    if taken:
        logging.info(f'Received page of results contains {taken} elements')

    return taken


def request_store_blob_trigger(storepath, request_def, skip):
    if request_def['method'] == 'GET':
        return request_by_getting_http_store_blob(storepath, request_def, skip)
    elif request_def['method'] == 'POST':
        return request_by_posting_http_store_blob(storepath, request_def, skip)
    else:
        problem = {'type': 'InvalidRequest',
                   'title': 'Invalid Request',
                   'status': 400}
        response = make_response(jsonify(problem), 415)
        response.headers['Content-Type'] = 'application/problem+json',
        return response


def append_pagination_to_url(request_def, skip):
    url = request_def['url']

    if 'pagination' in request_def:
        skip_val = skip if skip else 0
        take_param = request_def['pagination'].get('take_param', 'take')
        skip_param = request_def['pagination'].get('skip_param', 'skip')
        take_size = request_def['pagination']['take_size']
        return f'{url}?{take_param}={take_size}&{skip_param}={skip_val}'

    return url


def request_by_posting_http_store_blob(storepath, request_def, skip):
    media_type = request_def['body']['type']
    data = request_def['body']['content']
    cpHeaders = request_def['headers']
    cpHeaders['Content-Type'] = media_type
    cpHeaders.update(gather_authorization_headers(request_def))
    oauth1_config = 'authorization' in request_def and request_def['authorization'].get('type', '') == 'OAuth1'

    if media_type == 'application/json':
        request_data = json.dumps(data)
    else:
        request_data = data

    if 'authorization' in request_def and \
            'username' in request_def['authorization'] and \
            request_def['authorization'].get('type', '') == 'Soap':
        values_to_replace = {
            '_SOURCE': request_def['url'],
            '_USERNAME_': request_def['authorization']['username'],
            '_PASSWORD_': escape(get_authentication_secret())
        }
        for value in values_to_replace:
            request_data = request_data.replace(value,
                                                values_to_replace[value])
    if oauth1_config:
        consumer_secret = get_authentication_secret()
        consumer_key = config.CONSUMER_KEY
        oauth_1 = OAuth1(
            consumer_key,
            consumer_secret,
            signature_method='HMAC-SHA1'
        )

        data_response = requests.post(
            request_def['url'],
            auth=oauth_1,
            data=request_data,
            json=request_data,
            headers=cpHeaders
        )
    else:
        post_url = append_pagination_to_url(request_def, skip)
        logging.info(f'Requesting data by POST to {post_url}')
        data_response = requests.post(
            post_url,
            data=request_data,
            headers=cpHeaders,
        )

    if data_response.status_code != requests.codes.ok:
        logging.error(data_response.text)
        problem = {'type': 'DataError',
                   'title': 'Error requesting data',
                   'content': json.dumps(data_response.json()),
                   'status': 400}
        result_response = make_response(jsonify(problem), 400)
        result_response.headers['Content-Type'] = 'application/problem+json',
        return result_response, None

    headers = {'Content-Type': media_type}

    if 'pagination' in request_def:
        headers['X-Take-Skip'] = skip if skip else 0

    return connexion_app.handle_request(
        url=storepath,
        method='POST',
        headers=headers,
        data=data_response,
        type='response'
    ), data_response


def request_by_getting_http_store_blob(storepath, request_def, skip):
    logging.info('Python HTTP get_http_store_blob_trigger_func function processed a request')

    try:
        headers = request_def.get('headers', {})
        headers.update(gather_authorization_headers(request_def))
        get_url = append_pagination_to_url(request_def, skip)
        logging.info(f'Requesting data by GET to {get_url}')
        data_response = requests.get(get_url, headers=headers)
        data_response.raise_for_status()
    except requests.exceptions.HTTPError:
        logging.exception('Error retrieving data from [%s]', request_def['url'])
        problem = {'type': 'InternalCommError',
                   'title': 'Internal communications error',
                   'status': 500}
        result_response = make_response(jsonify(problem), 500)
        result_response.headers['Content-Type'] = 'application/problem+json',
        return result_response, None
    except requests.exceptions.ConnectionError:
        logging.warning('Error retrieving data from [%s]', request_def['url'])
        problem = {'type': 'InternalConfigError',
                   'title': 'Internal configuration incorrect',
                   'status': 500}
        result_response = make_response(jsonify(problem), 500)
        result_response.headers['Content-Type'] = 'application/problem+json',
        return result_response, None

    media_type = data_response.headers.get('Content-Type', 'application/json')
    headers = {'Content-Type': media_type}

    if 'pagination' in request_def:
        headers['X-Take-Skip'] = skip if skip else 0

    return connexion_app.handle_request(url=storepath, method='POST',
                                        headers=headers,
                                        data=data_response, type='response'), data_response


def http_receive_store_blob_trigger_func(request):
    logging.basicConfig(level=logging.info)
    logging.info('Python HTTP http_receive_store_blob_trigger_func function processed a request from %s.', request.path)

    cpHeaders = {}
    for key, value in request.headers:
        cpHeaders[key] = value

    return connexion_app.handle_request(url=request.path, method=request.method,
                                        headers=cpHeaders, data=request, type='request')
