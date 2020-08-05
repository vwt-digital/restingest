import os
import requests
import unittest


class E2ETest(unittest.TestCase):
    _domain = os.environ["domain"]

    def test_pos(self):
        self.assertTrue(0xDEADBEEF)

    def test_get_json_stg_store_generic(self):
        params = {
            'geturl': 'generics',
            'storepath': 'generics'
        }
        r = requests.post('https://europe-west1-' + self._domain + '.cloudfunctions.net/' + self._domain +
                          '-request-ingest-func', params=params)
        print(r.text)
        print(r.content)
        try:
            self.assertTrue(199 < r.status_code < 300)
        except AssertionError as e:
            raise type(e)(str(e) + "\n\n Full response:\n" + r.text)

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

    # def test_post_json_no_auth_urlencoded_pos(self):
    #     data = json.dumps({'ID': 1})
    #     headers = {
    #         "Content-type": "application/x-www-form-urlencoded"
    #     }
    #
    #     r = requests.post('https://europe-west1-' + self._domain + '.cloudfunctions.net/' + self._domain +
    #                       '-receive-ingest-func/store-json', data=data, headers=headers)
    #
    #     try:
    #         self.assertTrue(199 < r.status_code < 300)
    #     except AssertionError as e:
    #         raise type(e)(str(e) + "\n\n Full response:\n" + r.text)

    def test_post_json_no_auth_path_neg(self):
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

    def test_post_json_no_auth_schema_neg(self):
        payload = {
            'NOT_ID': "test"
        }

        r = requests.post('https://europe-west1-' + self._domain + '.cloudfunctions.net/' + self._domain +
                          '-receive-ingest-func/store-json', json=payload)
        try:
            self.assertFalse(199 < r.status_code < 300)
        except AssertionError as e:
            raise type(e)(str(e) + "\n\n Full response:\n" + r.text)

    def test_post_json_no_auth_data_type_neg(self):
        payload = "test"
        headers = {'Content-type': 'text/xml'}

        r = requests.post('https://europe-west1-' + self._domain + '.cloudfunctions.net/' + self._domain +
                          '-receive-ingest-func/store-json', data=payload, headers=headers)

        try:
            self.assertFalse(199 < r.status_code < 300)
        except AssertionError as e:
            raise type(e)(str(e) + "\n\n Full response:\n" + r.text)

    def test_post_xml_no_auth_generic_pos(self):
        payload = "<?xml version='1.0' encoding='utf-8'?><test attr1='attr1'>0</test>"
        headers = {'Content-type': 'application/xml'}

        r = requests.post('https://europe-west1-' + self._domain + '.cloudfunctions.net/' + self._domain +
                          '-receive-ingest-func/store-xml', data=payload, headers=headers)

        try:
            self.assertTrue(199 < r.status_code < 300)
        except AssertionError as e:
            raise type(e)(str(e) + "\n\n Full response:\n" + r.text)

    def test_post_xml_no_auth_data_type_neg(self):
        payload = {"json": "test"}

        headers = {"Content-type": "application/json"}
        r = requests.post('https://europe-west1-' + self._domain + '.cloudfunctions.net/' + self._domain +
                          '-receive-ingest-func/store-xml', data=payload, headers=headers)

        try:
            self.assertFalse(199 < r.status_code < 300)
        except AssertionError as e:
            raise type(e)(str(e) + "\n\n Full response:\n" + r.text)
