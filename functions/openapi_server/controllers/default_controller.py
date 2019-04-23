import datetime
import json
import copy

from flask import jsonify
from flask import make_response
from flask import current_app
from flask import request


def do_post(body, path):
    now = datetime.datetime.utcnow()
    timestamp = '%04d%02d%02dT%02d%02d%02dZ' % (now.year, now.month, now.day,
                                                now.hour, now.minute, now.second)
    destinationpath = '%s/%d/%d/%d/%s.json' % (path, now.year, now.month, now.day,
                                               timestamp)
    for cs in current_app.cloudstorage:
        cs.storeBlob(destinationpath, json.dumps(body))

    return {'path': destinationpath}


def generic_post(body):
    return make_response(jsonify(do_post(body, current_app.base_path + request.path)), 201)


def urencnt_post(body):
    return generic_post(body)


def urendesc_post(body):
    return generic_post(body)


def urenover_post(body):
    cumulative_response = {'paths': []}

    if 'x-pii-filter' in request.headers:
        pii_filters = json.loads(request.headers['x-pii-filter'])

        filtered_body = copy.deepcopy(body)
        for row in filtered_body['Rows']:
            for attr in pii_filters:
                if attr in row:
                    del row[attr]
        partial_response1 = do_post(filtered_body, current_app.base_path + '-' + request.headers['x-pii-filter-path']
                                    + request.path)
        cumulative_response['paths'].append(partial_response1)
        pass

    partial_response2 = do_post(body, current_app.base_path + request.path)
    cumulative_response['paths'].append(partial_response2)
    return make_response(json.dumps(cumulative_response), 201)
