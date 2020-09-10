import logging
import datetime
import json
import mimetypes
import requests
import uuid

from flask import jsonify
from flask import make_response
from flask import current_app
from flask import request

from defusedxml import ElementTree as defusedxml_ET
from lxml import etree as ET  # nosec


def apply_pii_filter(body, pii_filter):
    body_to_filter = body

    if type(body_to_filter) == list:
        filtered_body = []
        for item in body_to_filter:
            filtered_body.append(apply_pii_filter(item, pii_filter))
    elif type(body_to_filter) == dict:
        filtered_body = {}
        for attr in body_to_filter:
            if type(body_to_filter[attr]) == dict or type(body_to_filter[attr]) == list:
                filtered_body[attr] = apply_pii_filter(body_to_filter[attr], pii_filter)
            elif attr not in pii_filter:
                filtered_body[attr] = body_to_filter[attr]
    else:
        filtered_body = body_to_filter

    return filtered_body


def clear_keys_from_list(body, allowed):
    for k, v in body.copy().items():
        if k not in allowed:
            del body[k]
        if isinstance(v, dict):
            clear_keys_from_list(v, allowed)
    return body


def store_blobs(destination_path, blob_data, content_type, should_apply_pii_filter):
    url, method = request.base_url.replace(request.host_url, '/'), request.method.lower()
    json_schema = current_app.paths[url][method]['requestBody']['content']['application/json']['schema']['$ref']

    attribute_option, schema = None, None
    allowed_attributes = []

    if json_schema and current_app.schemas:
        schema = current_app.schemas[json_schema.split('/')[-1]]
        attribute_option = schema.get('x-strict-attributes')

    if schema and attribute_option == 'strict':

        def _get_schema_keys(dictionary):
            for key, value in dictionary.items():
                if type(value) is dict and key != 'properties':
                    allowed_attributes.append(key)
                if type(value) is dict:
                    _get_schema_keys(value)

        _get_schema_keys(schema)

    if content_type in ['text/xml', 'application/xml', 'application/xml-external-parsed-entity',
                        'text/xml-external-parsed-entity', 'application/xml-dtd']:

        # Run blob_data through defusedxml's ElementTree first to mitigate exposure from XML attacks
        safe_xml_tree = defusedxml_ET.fromstring(blob_data)

        # Run safe_xml_tree through lxml's ElementTree second to process
        xml_tree = ET.fromstring(defusedxml_ET.tostring(safe_xml_tree))  # nosec

        # Run through elements and select the local name for each tag to clean data of extra exposed namespaces
        for elem in xml_tree.getiterator():
            elem.tag = ET.QName(elem).localname

        blob_data = ET.tostring(xml_tree)

    if attribute_option == 'strict' and allowed_attributes:
        logging.info('Running with strict attribute rules')
        if type(blob_data) != list and type(blob_data) != dict:
            blob_data = json.loads(blob_data)
        blob_data = json.dumps(clear_keys_from_list(blob_data, allowed_attributes))

    if should_apply_pii_filter and (not attribute_option or attribute_option in ['filter', 'strict']):
        if type(blob_data) != list and type(blob_data) != dict:
            blob_data_to_filter = json.loads(blob_data)
        else:
            blob_data_to_filter = blob_data
        blob_data_pii = json.dumps(apply_pii_filter(blob_data_to_filter, current_app.__pii_filter_def__))
    else:
        blob_data_pii = blob_data

    if type(blob_data) == list or type(blob_data) == dict:
        blob_data = json.dumps(blob_data)

    logging.info('Storing blob data on path: {}'.format(destination_path))

    for cs in current_app.cloudstorage:
        cs.storeBlob(destination_path, blob_data_pii, content_type)

    for cs in current_app.cloudlogstorage:
        cs.storeBlob(destination_path, blob_data, content_type)


def generic_post(body):
    extension = mimetypes.guess_extension(request.mimetype)
    now = datetime.datetime.utcnow()

    timestamp = '%04d%02d%02dT%02d%02d%02dZ' % (now.year, now.month, now.day,
                                                now.hour, now.minute, now.second)

    take_skip = f"_{request.headers['X-Take-Skip']}" if 'X-Take-Skip' in request.headers else ''
    destination_path = '%s%s/%04d/%02d/%02d/%s%s-%s' % (current_app.base_path, request.path,
                                                        now.year, now.month, now.day, timestamp, take_skip,
                                                        str(uuid.uuid4()))

    try:
        if body:
            file_destination_path = '%s%s' % (destination_path, (extension if extension else ''))
            store_blobs(file_destination_path, body, request.mimetype,
                        (True if 'application/json' in request.mimetype else False))
        elif request.files:
            for index, file in enumerate(request.files, start=1):
                file_extension = mimetypes.guess_extension(request.files[file].content_type)
                file_destination_path = '%s/%s_%s%s' % (destination_path, timestamp, index,
                                                        (file_extension if file_extension else ''))
                store_blobs(file_destination_path, request.files[file].read(), request.files[file].content_type, False)
        elif request.form:
            for data in request.form:
                new_data = json.loads(request.form[data])

                for index, blob_data in enumerate(new_data, start=1):
                    file_destination_path = '%s/%s_%s%s' % (destination_path, timestamp, index,
                                                            (extension if extension else ''))
                    store_blobs(file_destination_path, blob_data, request.mimetype, False)
        elif request.data:
            file_destination_path = '%s%s' % (destination_path, (extension if extension else ''))
            store_blobs(file_destination_path, request.data, request.mimetype, ('application/json' in request.mimetype))
        else:
            raise ValueError('No correct body provided.')

        return make_response('Created', 201)
    except requests.exceptions.ConnectionError as error:
        logging.error(f"An exception occurred when uploading: {str(error)}")
        return make_response(jsonify(str(error)), 400)
    except Exception as error:
        logging.exception(error)
        return make_response(jsonify(str(error)), 400)


generic_post2 = generic_post
generic_post3 = generic_post
generic_post4 = generic_post
generic_post5 = generic_post
