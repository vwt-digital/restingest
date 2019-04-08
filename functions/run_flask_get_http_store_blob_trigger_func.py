from flask import Flask
from flask import request
from main import get_http_store_blob_trigger_func

app = Flask(__name__)


@app.route('/')
def test_get_http_func():
    return get_http_store_blob_trigger_func(request)
