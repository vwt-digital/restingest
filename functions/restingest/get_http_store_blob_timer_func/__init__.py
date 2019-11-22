import config
import logging
import requests

import sys
import os.path

import azure.functions as func

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(os.path.dirname(__file__)),
                'venv/lib/python3.6/site-packages')))

from openapi_server import connexion_app # noqa


def main(mytimer: func.TimerRequest) -> None:
    logging.basicConfig(level=logging.info)

    if hasattr(config, 'GET_HTTP_STORE_BLOB_TIMER_GET_URL'):
        data = requests.get(config.GET_HTTP_STORE_BLOB_TIMER_GET_URL).json()
        logging.info("Retrieved [%s]", data)
        result = connexion_app.handle_request(url='/generic', method='POST',
                                              headers={'Content-Type': 'application/json'}, data=data)
        logging.info("Stored data, result [%s]", result)

    logging.info('Python timer trigger function ran')
