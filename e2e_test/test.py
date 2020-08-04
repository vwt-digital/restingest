import unittest
import requests
import os


class E2ETest(unittest.TestCase):
    _domain = os.environ["domain"]

    def test_sunny_day(self):
        self.assertTrue(0xDEADBEEF)

    # def test_get_json_stg_store_generic(self):
    #     params = {
    #         'geturl': 'generics'
    #     }
    #     payload = {
    #         'geturl': 'generics'
    #     }
    #     r = requests.post('https://europe-west1-' + self._domain + '.cloudfunctions.net/' + self._domain +
    #                       '-request-ingest-func', params=params, json=payload)
    #     print(r.text)
    #     print(r.content)
    #     try:
    #         self.assertTrue(199 < r.status_code < 300)
    #     except AssertionError as e:
    #         raise type(e)(str(e) + "\n\n Full response:\n" + r.text)

    def test_post_json_no_auth_generic_pos(self):
        payload = {
            'ID': 1
        }

        r = requests.post('https://europe-west1-' + self._domain + '.cloudfunctions.net/' + self._domain +
                          '-receive-ingest-func/store-json', json=payload)

        try:
            self.assertTrue(199 < r.status_code < 300)
        except AssertionError as e:
            raise type(e)(str(e) + "\n\n Full response:\n" + r.text)

    def test_post_json_no_auth_generic_path_neg(self):
        payload = {
            'ID': 2
        }

        r = requests.post('https://europe-west1-' + self._domain + '.cloudfunctions.net/' + self._domain +
                          '-receive-ingest-func/', json=payload)
        try:
            self.assertFalse(199 < r.status_code < 300)
        except AssertionError as e:
            raise type(e)(str(e) + "\n\n Full response:\n" + r.text)

    def test_post_json_no_auth_no_payload(self):
        r = requests.post('https://europe-west1-' + self._domain + '.cloudfunctions.net/' + self._domain +
                          '-receive-ingest-func/store-json')
        try:
            self.assertFalse(199 < r.status_code < 300)
        except AssertionError as e:
            raise type(e)(str(e) + "\n\n Full response:\n" + r.text)

    # def test_post_json_no_auth_schema_neg(self):
    #     payload = {
    #         'NOT_ID': "test"
    #     }
    #
    #     r = requests.post('https://europe-west1-' + self._domain + '.cloudfunctions.net/' + self._domain +
    #                       '-receive-ingest-func/store-json', json=payload)
    #     try:
    #         self.assertFalse(199 < r.status_code < 300)
    #     except AssertionError as e:
    #         raise type(e)(str(e) + "\n\n Full response:\n" + r.text)
