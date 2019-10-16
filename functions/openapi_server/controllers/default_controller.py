import datetime
import json
import copy
import mimetypes

from flask import jsonify
from flask import make_response
from flask import current_app
from flask import request


def apply_pii_filter(body, pii_filter):
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


def generic_post(body):
    extension = mimetypes.guess_extension(request.mimetype)
    now = datetime.datetime.utcnow()
    timestamp = '%04d%02d%02dT%02d%02d%02dZ' % (now.year, now.month, now.day,
                                                now.hour, now.minute, now.second)
    destinationpath = '%s%s/%04d/%02d/%02d/%s%s' % (current_app.base_path, request.path,
                                                    now.year, now.month, now.day,
                                                    timestamp, (extension if extension else ''))

    for cs in current_app.cloudstorage:
        cs.storeBlob(destinationpath, json.dumps(apply_pii_filter(copy.deepcopy(body),
                                                                  current_app.__pii_filter_def__)),
                                                                  request.mimetype)

    for cs in current_app.cloudlogstorage:
        cs.storeBlob(destinationpath,
                     json.dumps(copy.deepcopy(body)),
                     request.mimetype)

    return make_response(jsonify({'path': destinationpath}), 201)


def generic_post2(body):
    return generic_post(body)


def generic_post3(body):
    return generic_post(body)
