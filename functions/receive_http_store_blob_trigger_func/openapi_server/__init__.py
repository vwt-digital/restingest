import logging
import connexion

from flask_testing import TestCase

class BaseApp(TestCase):

    def create_app(self):
        logging.getLogger('connexion.operation').setLevel('INFO')
        app = connexion.App(__name__, specification_dir='openapi/')
        app.add_api('openapi.yaml')
        return app.app

    def handle_request(self, url, method, headers, data, content_type='application/json'):
        return self.client.open(url=url,
            method=method,
            headers=headers,
            data=data,
            content_type=content_type)


connexion_app = BaseApp()
app = connexion_app.create_app()
