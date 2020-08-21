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


def store_blobs(destination_path, blob_data, content_type, should_apply_pii_filter):
    if content_type in ['text/xml', 'application/xml', 'application/xml-external-parsed-entity',
                        'text/xml-external-parsed-entity', 'application/xml-dtd']:

        xml_tree = ET.fromstring(blob_data)  # nosec
        ET.strip_tags(xml_tree, ET.Comment)

        for elem in xml_tree.getiterator():
            try:
                elem.tag = ET.QName(elem).localname
            except ValueError:
                continue

        blob_data = ET.tostring(xml_tree)

    if should_apply_pii_filter:
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

    timestamp = 'T%02d%02d%02dZ' % (now.hour, now.minute, now.second)
    date_timestamp = '%04d%02d%02d%s' % (now.year, now.month, now.day, timestamp)

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
                file_destination_path = '%s/%s_%s%s' % (destination_path, date_timestamp, index,
                                                        (file_extension if file_extension else ''))
                store_blobs(file_destination_path, request.files[file].read(), request.files[file].content_type, False)
        elif request.form:
            for data in request.form:
                new_data = json.loads(request.form[data])

                for index, blob_data in enumerate(new_data, start=1):
                    file_destination_path = '%s/%s_%s%s' % (destination_path, date_timestamp, index,
                                                            (extension if extension else ''))
                    store_blobs(file_destination_path, blob_data, request.mimetype, False)
        elif request.data:
            file_destination_path = '%s%s' % (destination_path, (extension if extension else ''))
            store_blobs(file_destination_path, request.data, request.mimetype, False)
        else:
            raise ValueError('No correct body provided.')

        return make_response(jsonify({'path': destination_path}), 201)
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
