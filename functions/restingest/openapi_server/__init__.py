import logging
import connexion
import config

from flask import current_app
from flask_cors import CORS
from azurecloudstorage import AzureCloudStorage
from googlecloudstorage import GoogleCloudStorage

logging.basicConfig(level=logging.INFO)


# BaseApp wraps the Connexion app, also exposing the handle_request function to allow calling from
# cloud lambda/functions
class BaseApp:

    def __init__(self):
        self.cxnapp = connexion.App(__name__, specification_dir='openapi/')
        self.cxnapp.add_api('openapi.yaml')
        CORS(self.cxnapp.app)
        with self.cxnapp.app.app_context():
            current_app.__pii_filter_def__ = None
            current_app.base_path = config.BASE_PATH
            current_app.cloudstorage = []
            current_app.cloudlogstorage = []

            if hasattr(config, 'AZURE_STORAGE_ACCOUNT'):
                current_app.cloudstorage.append(AzureCloudStorage(config.AZURE_STORAGE_ACCOUNT,
                                                                  config.AZURE_STORAGE_KEY,
                                                                  config.AZURE_STORAGE_CONTAINER))
            if hasattr(config, 'GOOGLE_STORAGE_BUCKET'):
                current_app.cloudstorage.append(GoogleCloudStorage(config.GOOGLE_STORAGE_BUCKET))
            if hasattr(config, 'GOOGLE_LOG_BUCKET'):
                current_app.cloudlogstorage.append(GoogleCloudStorage(config.GOOGLE_LOG_BUCKET))

    def get_cxnapp(self):
        return self.cxnapp

    # handle_request uses the flask test_client to call the handler for a http request
    # This can be used to wrap the Connexion handler in a cloud lambda/function.
    def handle_request(self, url, method, headers, data, type):
        if not self.cxnapp.app.__pii_filter_def__:
            raw = self.cxnapp.app.test_client().open(path='/openapi.json', method='GET',
                                                     content_type='application/json').json
            if 'x-pii-filter' in raw:
                self.cxnapp.app.__pii_filter_def__ = raw['x-pii-filter']
            else:
                self.cxnapp.app.__pii_filter_def__ = []
                logging.debug("Doing [%s] to [%s]", method, url)
        if method == 'POST' or method == 'OPTIONS' or method == 'GET':
            if 'request' in type:
                if data.is_json:
                    req_body = data.get_json(silent=True)
                    return self.get_cxnapp().app.test_client().open(path=url, method=method, headers=headers, json=req_body,
                                                                    content_type='application/json')
                else:
                    if data.files:
                        req_body = data.files
                    else:
                        req_body = data.form if data.form else data.data

                    return self.get_cxnapp().app.test_client().open(path=url, method=method, headers=headers, data=req_body,
                                                                    content_type=(data.mimetype if data.mimetype else ''))
            elif 'response' in type:
                if 'Content-Type' in headers \
                        and headers['Content-Type'] == 'application/json':
                    req_body = data.json()
                    return self.get_cxnapp().app.test_client().open(path=url, method=method, headers=headers, json=req_body,
                                                                    content_type='application/json')
                else:
                    req_body = data.content
                    return self.get_cxnapp().app.test_client() \
                        .open(path=url, method=method, headers=headers, data=req_body,
                              content_type=(headers['Content-Type'] if 'Content-Type' in headers else ''))
        else:
            raise NotImplementedError


connexion_app = BaseApp()
app = connexion_app.get_cxnapp().app
