import logging
import datetime
import json
import mimetypes

from flask import jsonify
from flask import make_response
from flask import current_app
from flask import request


def apply_pii_filter(body, pii_filter):
    if type(body) != list and type(body) != dict:
        body = json.loads(body)

    if type(body) == list:
        for item in body:
            apply_pii_filter(item, pii_filter)
    elif type(body) == dict:
        for attr in body.copy():
            if type(body[attr]) == dict:
                apply_pii_filter(body[attr], pii_filter)
            elif type(body[attr]) == list:
                apply_pii_filter(body[attr], pii_filter)
            elif attr in pii_filter:
                del body[attr]
    return body


def store_blobs(destination_path, blob_data, content_type, pii_filter):
    blob_data_pii = json.dumps(apply_pii_filter(blob_data, current_app.__pii_filter_def__)) if pii_filter \
                    else blob_data

    blob_data = json.dumps(blob_data) if type(blob_data) != list or type(blob_data) != dict else blob_data

    for cs in current_app.cloudstorage:
        cs.storeBlob(destination_path, blob_data_pii, content_type)

    for cs in current_app.cloudlogstorage:
        cs.storeBlob(destination_path, blob_data, content_type)


def generic_post(body):
    extension = mimetypes.guess_extension(request.mimetype)
    now = datetime.datetime.utcnow()
    timestamp = '%04d%02d%02dT%02d%02d%02dZ' % (now.year, now.month, now.day,
                                                now.hour, now.minute, now.second)
    destination_path = '%s%s/%04d/%02d/%02d' % (current_app.base_path, request.path,
                                                now.year, now.month, now.day)

    try:
        if body:
            file_destination_path = '%s/%s%s' % (destination_path, timestamp, (extension if extension else ''))
            store_blobs(file_destination_path, body, request.mimetype,
                        (True if 'application/json' in request.mimetype else False))
        elif request.files:
            sub_destination_path = '%s%s/%04d/%02d/%02d' % (current_app.base_path, request.path, now.year,
                                                            now.month, now.day)
            if len(request.files) > 1:
                sub_destination_path = '%s/%s' % (sub_destination_path, timestamp)

            for index, file in enumerate(request.files, start=1):
                file_extension = mimetypes.guess_extension(request.files[file].content_type)
                file_destination_path = '%s/%s_%s%s' % (sub_destination_path, timestamp, index,
                                                        (file_extension if file_extension else ''))
                store_blobs(file_destination_path, request.files[file].read(), request.files[file].content_type, False)
        elif request.form:
            for data in request.form:
                new_data = json.loads(request.form[data])
                sub_destination_path = '%s%s/%04d/%02d/%02d' % (current_app.base_path, request.path, now.year,
                                                                now.month, now.day)
                if len(new_data) > 1:
                    sub_destination_path = '%s/%s' % (sub_destination_path, timestamp)

                for index, blob_data in enumerate(new_data, start=1):
                    file_destination_path = '%s/%s_%s%s' % (sub_destination_path, timestamp, index,
                                                            (extension if extension else ''))
                    store_blobs(file_destination_path, blob_data, request.mimetype, False)
        elif request.data:
            file_destination_path = '%s/%s%s' % (destination_path, timestamp, (extension if extension else ''))
            store_blobs(file_destination_path, request.data, request.mimetype, False)
        else:
            raise ValueError('No correct body provided.')

        return make_response(jsonify({'path': destination_path}), 201)
    except Exception as error:
        logging.exception(error)
        return make_response(jsonify(str(error)), 400)


def generic_post2(body):
    return generic_post(body)


def generic_post3(body):
    return generic_post(body)
