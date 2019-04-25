import logging

import connexion
from flask_testing import TestCase
from flask import current_app


class BaseTestCase(TestCase):

    def create_app(self):
        logging.getLogger('connexion.operation').setLevel('ERROR')
        app = connexion.App(__name__, specification_dir='../openapi/')
        app.add_api('openapi.yaml')
        with app.app.app_context():
            current_app.base_path = 'base/path'
            current_app.cloudstorage = []
        return app.app
