from openapi3_fuzzer import FuzzIt
from openapi_server.test import BaseTestCase


class TestvAPI(BaseTestCase):

    def test_fuzzing(self):
        FuzzIt("functions/restingest/openapi_server/openapi/openapi.yaml", '', self)
