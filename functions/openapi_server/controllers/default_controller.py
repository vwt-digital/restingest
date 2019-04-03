import datetime
import json

from flask import jsonify
from flask import make_response
from flask import current_app


def generic_post(body):
    now = datetime.datetime.utcnow()
    timestamp = '%04d%02d%02dT%02d%02d%02dZ' % (now.year, now.month, now.day,
                                                now.hour, now.minute, now.second)
    destinationpath = '%s/%d/%d/%d/%s.json' % (current_app.base_path, now.year, now.month, now.day,
                                               timestamp)
    for cs in current_app.cloudstorage:
        cs.storeBlob(destinationpath, json.dumps(body))

    return make_response(jsonify({'path': destinationpath}), 201)
