import json
import os
import requests
# from requests_oauthlib import OAuth2
import unittest
from google.cloud import storage


class E2ETest(unittest.TestCase):
    _domain = os.environ["domain"]
    _storage_bucket = os.environ["bucket"]
    _project_id = os.environ["project_id"]
    _test_token = os.environ["test_token"]
    storage_client = storage.Client()
    _blob_path = ''

    def test_pos(self):
        self.assertTrue(0xDEADBEEF)

    def test_get_json_stg_store_generic(self):
        """
        Creates post request with parameters to get json and stores into storage in specific path.
        Generic functionality, should pass.
        """
        params = {
            'geturl': 'generics-json',
            'storepath': 'generics'
        }
        r = requests.post('https://europe-west1-' + self._domain + '.cloudfunctions.net/' + self._domain +
                          '-request-ingest-func', params=params)
        self.__class__._blob_path = json.loads(r.text)['path']
        try:
            self.assertTrue(199 < r.status_code < 300)
        except AssertionError as e:
            raise type(e)(str(e) + "\n\n Full response:\n" + r.text)

    def test_get_pii_on_json(self):
        """
        Uses blob stored in last test step.
        Generic functionality, should pass.
        """
        blob = self.storage_client.get_bucket(self._storage_bucket).blob(self.__class__._blob_path + '.json')
        data = json.loads(blob.download_as_string(client=None))
        try:
            def does_nested_key_exists(nested_dict, nested_key):
                exists = nested_key in nested_dict
                if not exists:
                    for key, value in nested_dict.items():
                        if isinstance(value, dict):
                            exists = exists or does_nested_key_exists(value, nested_key)
                return exists

            self.assertFalse(does_nested_key_exists(data, 'title'))
            self.assertFalse(does_nested_key_exists(data, 'date'))
        except AssertionError as e:
            raise type(e)(str(e))

    def test_get_json_stg_store_no_storage_path(self):
        """
        Creates post request with parameter to get json and stores into storage in base path.
        No storepath is given, should fail.
        """
        params = {
            'geturl': 'generics-json',
        }
        r = requests.post('https://europe-west1-' + self._domain + '.cloudfunctions.net/' + self._domain +
                          '-request-ingest-func', params=params)
        try:
            self.assertFalse(199 < r.status_code < 300)
        except AssertionError as e:
            raise type(e)(str(e) + "\n\n Full response:\n" + r.text)

    def test_get_json_stg_store_invalid_parameter_values(self):
        """
        Creates post request with parameter to get json and stores into storage in base path.
        Invalid parameters are given, should fail.
        """
        get_url = 'generics-json'
        key_store_path = 'storepath'
        key_get_url = 'geturl'
        param_list = {1: {key_get_url: 1, key_store_path: 'generics'}, 2: {key_get_url: get_url, key_store_path: '_'},
                      3: {key_get_url: get_url,
                          key_store_path: 'AAAAAAAAAAAAAAAAAAAAAAAAAAAAAaaaaaaaaaaaaaaaaaaaa'
                                          '############@@@@AAAAAAAAAAAAEEEEEEEEEEEEEEEEEEEEEEEE '}}
        for params in param_list.values():
            print('Testing with geturl: ' + str(params['geturl']) + ' and storepath: ' + str(params['storepath']))
            r = requests.post('https://europe-west1-' + self._domain + '.cloudfunctions.net/' + self._domain +
                              '-request-ingest-func', params=params)
            try:
                self.assertFalse(199 < r.status_code < 300)
            except AssertionError as e:
                raise type(e)(str(e) + "\n\n Full response:\n" + r.text)

    def test_get_json_stg_store_invalid_parameter_names(self):
        """
        Creates post request with parameter to get json and stores into storage in base path.
        Invalid parameters are given, should fail.
        """
        params = {
            'NO_ID': 'no_id',
            'Args': 'args'
        }
        r = requests.post('https://europe-west1-' + self._domain + '.cloudfunctions.net/' + self._domain +
                          '-request-ingest-func', params=params)
        try:
            self.assertFalse(199 < r.status_code < 300)
        except AssertionError as e:
            raise type(e)(str(e) + "\n\n Full response:\n" + r.text)

    def test_get_json_stg_store_no_params(self):
        """
        Creates post request without parameters to get json and stores into storage.
        No parameters passed, should fail.
        """
        r = requests.post('https://europe-west1-' + self._domain + '.cloudfunctions.net/' + self._domain +
                          '-request-ingest-func')
        try:
            self.assertFalse(199 < r.status_code < 300)
        except AssertionError as e:
            raise type(e)(str(e) + "\n\n Full response:\n" + r.text)

    def test_get_xml_stg_store_generic(self):
        """
        Creates post request with parameters to get xml and stores into storage in specific path.
        Generic functionality, should pass.
        """
        params = {
            'geturl': 'generics-xml',
            'storepath': 'generics'
        }
        r = requests.post('https://europe-west1-' + self._domain + '.cloudfunctions.net/' + self._domain +
                          '-request-ingest-func', params=params)
        try:
            self.assertTrue(199 < r.status_code < 300)
        except AssertionError as e:
            raise type(e)(str(e) + "\n\n Full response:\n" + r.text)

    def test_post_json_no_auth_generic_pos(self):
        """
        Positive test with basic configuration
        """
        payload = {
            'ID': 1
        }

        r = requests.post('https://europe-west1-' + self._domain + '.cloudfunctions.net/' + self._domain +
                          '-receive-ingest-func/store-json', json=payload)

        try:
            self.assertTrue(199 < r.status_code < 300)
        except AssertionError as e:
            raise type(e)(str(e) + "\n\n Full response:\n" + r.text)

    #
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
        """
        Negative test for posting with no path
        """
        payload = {
            'ID': 2
        }

        r = requests.post('https://europe-west1-' + self._domain + '.cloudfunctions.net/' + self._domain +
                          '-receive-ingest-func/', json=payload)
        try:
            self.assertFalse(199 < r.status_code < 300)
        except AssertionError as e:
            raise type(e)(str(e) + "\n\n Full response:\n" + r.text)

    def test_post_json_no_auth_no_payload_neg(self):
        """
        Negative test for posting without a request body (payload)
        """
        r = requests.post('https://europe-west1-' + self._domain + '.cloudfunctions.net/' + self._domain +
                          '-receive-ingest-func/store-json')
        try:
            self.assertFalse(199 < r.status_code < 300)
        except AssertionError as e:
            raise type(e)(str(e) + "\n\n Full response:\n" + r.text)

    def test_post_json_no_auth_schema_neg(self):
        """
        Negative test for incorrect schema
        """
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
        """
        Negative test which expects store-json to not accept xml
        """
        payload = "test"
        headers = {'Content-type': 'text/xml'}

        r = requests.post('https://europe-west1-' + self._domain + '.cloudfunctions.net/' + self._domain +
                          '-receive-ingest-func/store-json', data=payload, headers=headers)

        try:
            self.assertFalse(199 < r.status_code < 300)
        except AssertionError as e:
            raise type(e)(str(e) + "\n\n Full response:\n" + r.text)

    def test_post_xml_no_auth_generic_pos(self):
        """
        Positive test with basic config
        """
        payload = "<?xml version='1.0' encoding='utf-8'?><test attr1='attr1'>0</test>"
        headers = {'Content-type': 'application/xml'}

        r = requests.post('https://europe-west1-' + self._domain + '.cloudfunctions.net/' + self._domain +
                          '-receive-ingest-func/store-xml', data=payload, headers=headers)

        try:
            self.assertTrue(199 < r.status_code < 300)
        except AssertionError as e:
            raise type(e)(str(e) + "\n\n Full response:\n" + r.text)

    def test_post_xml_no_auth_data_type_neg(self):
        """
        Negative test which expects store-xml to not accept application/json
        """
        payload = {"json": "test"}

        headers = {"Content-type": "application/json"}
        r = requests.post('https://europe-west1-' + self._domain + '.cloudfunctions.net/' + self._domain +
                          '-receive-ingest-func/store-xml', data=payload, headers=headers)

        try:
            self.assertFalse(199 < r.status_code < 300)
        except AssertionError as e:
            raise type(e)(str(e) + "\n\n Full response:\n" + r.text)

    def test_post_json_oauth_generic_pos(self):
        """
        Positive test which posts json using oauth
        """
        oauth_headers = {"Content-Type: application/x-www-form-urlencoded"}
        oauth_data = {"client_id": "47ae5f24-b920-4d55-b67c-933d53d23cad",
                      "scope": "https://" + self._project_id,
                      "client_secret": self._test_token,
                      "grant-type": "client_credentials"}
        token = requests.post('https://login.microsoftonline.com/be36ab0a-ee39-47de-9356-a8a501a9c832/'
                              'oauth2/v2.0/token', headers=oauth_headers, data=oauth_data)

        headers = {"Authorization": token}
        payload = {"ID": "1"}
        r = requests.post('https://europe-west1-' + self._domain + '.cloudfunctions.net/' + self._domain +
                          '-receive-ingest-func/store-json-oauth', headers=headers, data=payload)

        try:
            self.assertTrue(199 < r.status_code < 300)
        except AssertionError as e:
            raise type(e)(str(e) + "\n\n Full response:\n" + r.text)
