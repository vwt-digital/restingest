import datetime
import json
import copy

from flask import jsonify
from flask import make_response
from flask import current_app
from flask import request


def apply_pii_filter(body, pii_filter):
    if type(body) == dict or type(body) == list:
        for attr in body.copy():
            if type(body[attr]) == dict:
                apply_pii_filter(body[attr], pii_filter)
            elif type(body[attr]) == list:
                for item in body[attr]:
                    apply_pii_filter(item, pii_filter)
            elif attr in pii_filter:
                del body[attr]
    return body


def generic_post(body):
    now = datetime.datetime.utcnow()
    timestamp = '%04d%02d%02dT%02d%02d%02dZ' % (now.year, now.month, now.day,
                                                now.hour, now.minute, now.second)
    destinationpath = '%s%s/%d/%d/%d/%s.json' % (current_app.base_path, request.path, now.year, now.month, now.day,
                                                 timestamp)
    for cs in current_app.cloudstorage:
        if cs.is_log_storage():
            cs.storeBlob(destinationpath, json.dumps(copy.deepcopy(body)))
        else:
            cs.storeBlob(destinationpath, json.dumps(apply_pii_filter(copy.deepcopy(body),
                                                                      current_app.__pii_filter_def__)))

    return make_response(jsonify({'path': destinationpath}), 201)


def generic_post2(body):
    return generic_post(body)


def generic_post3(body):
    return generic_post(body)
