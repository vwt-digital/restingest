from flask import Flask
from flask import request
from main import http_request_store_blob_trigger_func
import logging

logging.basicConfig(level=logging.INFO)

app = Flask(__name__)


@app.route('/')
def test_get_http_func():
    #    return get_http_store_blob_trigger_func(request)
    return http_request_store_blob_trigger_func(request)
