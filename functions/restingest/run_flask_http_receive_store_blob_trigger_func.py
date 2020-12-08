from flask import Flask
from flask import request
from main import http_receive_store_blob_trigger_func
import logging

logging.basicConfig(level=logging.INFO)

app = Flask(__name__)


@app.route('/<path:u_path>', methods=['POST'])
def test_get_http_func(u_path):
    return http_receive_store_blob_trigger_func(request)
