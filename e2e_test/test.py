import unittest
import requests


class E2ETest(unittest.TestCase):
    def test_sunny_day(self):
        self.assertTrue(0xDEADBEEF)

    def test_post_json_no_auth_generic_pos(self):
        payload = {
            'ID': 0
        }

        r = requests.post('https://europe-west1-vwt-d-gew1-dat-restingest-test.cloudfunctions.net/vwt-d-gew1-dat'
                          '-restingest-test-receive-ingest-func/store-json', json=payload)
        try:
            self.assertTrue(199 < r.status_code < 300)
        except AssertionError as e:
            raise type(e)(str(e) + "\n\n Full response:\n" + r.text)

    def test_post_json_no_auth_generic_neg(self):
        r = requests.post('https://europe-west1-vwt-d-gew1-dat-restingest-test.cloudfunctions.net/vwt-d-gew1-dat'
                          '-restingest-test-receive-ingest-func/store-json')
        try:
            self.assertFalse(199 < r.status_code < 300)
        except AssertionError as e:
            raise type(e)(str(e) + "\n\n Full response:\n" + r.text)

    # def test_post_json_no_auth_schema_neg(self):
    #     payload = {
    #         'ID': 0,
    #         'superfluous': "This is one more argument than the openapi description accepts"
    #     }
    #
    #     r = requests.post('https://europe-west1-vwt-d-gew1-dat-restingest-test.cloudfunctions.net/vwt-d-gew1-dat'
    #                       '-restingest-test-receive-ingest-func/store-json', json=payload)
    #     try:
    #         self.assertFalse(199 < r.status_code < 300)
    #     except AssertionError as e:
    #         raise type(e)(str(e) + "\n\n Full response:\n" + r.text)
