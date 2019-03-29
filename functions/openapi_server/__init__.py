import logging
import connexion


# BaseApp wraps the Connexion app, also exposing the handle_request function to allow calling from
# cloud lambda/functions
class BaseApp:

    def __init__(self):
        logging.getLogger('connexion.operation').setLevel('INFO')
        self.cxnapp = connexion.App(__name__, specification_dir='openapi/')
        self.cxnapp.add_api('openapi.yaml')

    def get_cxnapp(self):
        return self.cxnapp

    # handle_request uses the flask test_client to call the handler for a http request
    # This can be used to wrap the Connexion handler in a cloud lambda/function.
    def handle_request(self, url, method, headers, data, content_type='application/json'):
        if method == 'POST':
            logging.debug("Doing post %s %s", url, method)
            logging.debug("headers %s", headers)
            logging.debug("data %s", data)
            return self.get_cxnapp().app.test_client().open(path=url,
                                                            method=method,
                                                            headers=headers,
                                                            json=data,
                                                            content_type=content_type)
        else:
            raise NotImplementedError


connexion_app = BaseApp()
app = connexion_app.get_cxnapp().app
