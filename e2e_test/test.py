import datetime
import json
import os
import unittest

import config
import requests
from google.cloud import secretmanager, storage


def get_secret():

    client = secretmanager.SecretManagerServiceClient()

    secret_name = client.secret_version_path(
        os.environ["domain"], os.environ["key_name"], "latest"
    )

    response = client.access_secret_version(secret_name)
    payload = response.payload.data.decode("UTF-8").replace("\n", "")

    return payload


secret = get_secret()


def does_nested_key_exists(nested_dict, nested_key):
    exists = nested_key in nested_dict
    if not exists:
        for key, value in nested_dict.items():
            if isinstance(value, dict):
                exists = exists or does_nested_key_exists(value, nested_key)
    return exists


class E2ETest(unittest.TestCase):
    _domain = os.environ["domain"]
    _storage_bucket = os.environ["bucket"]
    storage_client = storage.Client()
    _blob_path = ""

    def test_pos(self):
        self.assertTrue(0xDEADBEEF)

    def test_get_json_stg_store_generic(self):
        """
        Creates post request with parameters to get json and stores into storage in specific path.
        Generic functionality, should pass.
        """
        params = {"geturl": "generics-json", "storepath": "generics-json"}
        r = requests.post(
            "https://europe-west1-"
            + self._domain
            + ".cloudfunctions.net/"
            + self._domain
            + "-request-ingest-func/generics-json",
            params=params,
        )
        try:
            self.assertTrue(199 < r.status_code < 300)
        except AssertionError as e:
            raise type(e)(str(e) + "\n\n Full response:\n" + r.text)

    def test_get_pii_on_json(self):
        """
        Uses blob stored in last test step.
        Generic functionality, should pass.
        """
        now = datetime.datetime.utcnow()
        location = "test/e2e/generics-json/%04d/%02d/%02d" % (
            now.year,
            now.month,
            now.day,
        )
        blobs = [
            (blob, blob.updated)
            for blob in self.storage_client.list_blobs(
                self._storage_bucket,
                prefix=location,
            )
        ]
        blob = sorted(blobs, key=lambda tup: tup[1])[-1][0]
        data = json.loads(blob.download_as_string(client=None))
        try:
            self.assertFalse(does_nested_key_exists(data, "type"))
        except AssertionError as e:
            raise type(e)(str(e))

    def test_get_json_stg_store_generic_strict(self):
        """
        Creates post request with parameters to get json and stores into storage in specific path.
        Generic functionality, should pass.
        """
        params = {"geturl": "generics-json-strict", "storepath": "generics-json-strict"}
        r = requests.post(
            "https://europe-west1-"
            + self._domain
            + ".cloudfunctions.net/"
            + self._domain
            + "-request-ingest-func/generics-json-strict",
            params=params,
        )
        try:
            self.assertTrue(199 < r.status_code < 300)
        except AssertionError as e:
            raise type(e)(str(e) + "\n\n Full response:\n" + r.text)

    def test_get_strict_filter_on_json(self):
        """
        Uses blob stored in last test step.
        Generic functionality, should pass.
        """
        now = datetime.datetime.utcnow()
        location = "test/e2e/generics-json-strict/%04d/%02d/%02d" % (
            now.year,
            now.month,
            now.day,
        )
        blobs = [
            (blob, blob.updated)
            for blob in self.storage_client.list_blobs(
                self._storage_bucket,
                prefix=location,
            )
        ]
        blob = sorted(blobs, key=lambda tup: tup[1])[-1][0]
        data = json.loads(blob.download_as_string(client=None))
        try:
            self.assertFalse(does_nested_key_exists(data, "items"))
            self.assertFalse(does_nested_key_exists(data, "author"))
        except AssertionError as e:
            raise type(e)(str(e))

    def test_get_json_stg_store_no_storage_path(self):
        """
        Creates post request with parameter to get json and stores into storage in base path.
        No storepath is given, should fail.
        """
        params = {
            "geturl": "generics-json",
        }
        r = requests.post(
            "https://europe-west1-"
            + self._domain
            + ".cloudfunctions.net/"
            + self._domain
            + "-request-ingest-func/generics-json",
            params=params,
        )
        try:
            self.assertFalse(199 < r.status_code < 300)
        except AssertionError as e:
            raise type(e)(str(e) + "\n\n Full response:\n" + r.text)

    def test_get_json_stg_store_invalid_parameter_values(self):
        """
        Creates post request with parameter to get json and stores into storage in base path.
        Invalid parameters are given, should fail.
        """
        get_url = "generics-json"
        key_store_path = "storepath"
        key_get_url = "geturl"
        param_list = {
            1: {key_get_url: 1, key_store_path: "generics"},
            2: {key_get_url: get_url, key_store_path: "_"},
            3: {
                key_get_url: get_url,
                key_store_path: "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAaaaaaaaaaaaaaaaaaaaa"
                "############@@@@AAAAAAAAAAAAEEEEEEEEEEEEEEEEEEEEEEEE ",
            },
        }
        for params in param_list.values():
            print(
                "Testing with geturl: "
                + str(params["geturl"])
                + " and storepath: "
                + str(params["storepath"])
            )
            r = requests.post(
                "https://europe-west1-"
                + self._domain
                + ".cloudfunctions.net/"
                + self._domain
                + "-request-ingest-func/generics-json",
                params=params,
            )
            try:
                self.assertFalse(199 < r.status_code < 300)
            except AssertionError as e:
                raise type(e)(str(e) + "\n\n Full response:\n" + r.text)

    def test_get_json_stg_store_invalid_parameter_names(self):
        """
        Creates post request with parameter to get json and stores into storage in base path.
        Invalid parameters are given, should fail.
        """
        params = {"NO_ID": "no_id", "Args": "args"}
        r = requests.post(
            "https://europe-west1-"
            + self._domain
            + ".cloudfunctions.net/"
            + self._domain
            + "-request-ingest-func/generics-json",
            params=params,
        )
        try:
            self.assertFalse(199 < r.status_code < 300)
        except AssertionError as e:
            raise type(e)(str(e) + "\n\n Full response:\n" + r.text)

    def test_get_json_stg_store_no_params(self):
        """
        Creates post request without parameters to get json and stores into storage.
        No parameters passed, should fail.
        """
        r = requests.post(
            "https://europe-west1-"
            + self._domain
            + ".cloudfunctions.net/"
            + self._domain
            + "-request-ingest-func/generics-json"
        )
        try:
            self.assertFalse(199 < r.status_code < 300)
        except AssertionError as e:
            raise type(e)(str(e) + "\n\n Full response:\n" + r.text)

    def test_get_text_stg_store_generic(self):
        """
        Creates post request with parameters to get text and stores into storage in specific path.
        Generic functionality, should pass.
        """
        params = {"geturl": "generics-text", "storepath": "generics-text"}
        r = requests.post(
            "https://europe-west1-"
            + self._domain
            + ".cloudfunctions.net/"
            + self._domain
            + "-request-ingest-func/generics-text",
            params=params,
        )
        try:
            self.assertTrue(199 < r.status_code < 300)
        except AssertionError as e:
            raise type(e)(str(e) + "\n\n Full response:\n" + r.text)

    def test_get_xml_stg_store_generic(self):
        """
        Creates post request with parameters to get xml and stores into storage in specific path.
        Generic functionality, should pass.
        """
        params = {"geturl": "generics-xml", "storepath": "generics-xml"}
        r = requests.post(
            "https://europe-west1-"
            + self._domain
            + ".cloudfunctions.net/"
            + self._domain
            + "-request-ingest-func/generics-xml",
            params=params,
        )
        try:
            self.assertTrue(199 < r.status_code < 300)
        except AssertionError as e:
            raise type(e)(str(e) + "\n\n Full response:\n" + r.text)

    def test_post_json_no_auth_generic_pos(self):
        """
        Positive test with basic configuration
        """
        payload = {"ID": 1}
        headers = {"Content-Type": "application/json"}

        r = requests.post(
            "https://europe-west1-"
            + self._domain
            + ".cloudfunctions.net/"
            + self._domain
            + "-receive-ingest-func/store-json",
            data=json.dumps(payload),
            headers=headers,
        )

        try:
            self.assertTrue(199 < r.status_code < 300)
        except AssertionError as e:
            raise type(e)(str(e) + "\n\n Full response:\n" + r.text)

    def test_post_json_no_auth_path_neg(self):
        """
        Negative test for posting with no path
        """
        payload = {"ID": 2}

        r = requests.post(
            "https://europe-west1-"
            + self._domain
            + ".cloudfunctions.net/"
            + self._domain
            + "-receive-ingest-func/",
            json=payload,
        )
        try:
            self.assertFalse(199 < r.status_code < 300)
        except AssertionError as e:
            raise type(e)(str(e) + "\n\n Full response:\n" + r.text)

    def test_post_json_no_auth_no_payload_neg(self):
        """
        Negative test for posting without a request body (payload)
        """
        r = requests.post(
            "https://europe-west1-"
            + self._domain
            + ".cloudfunctions.net/"
            + self._domain
            + "-receive-ingest-func/store-json"
        )
        try:
            self.assertFalse(199 < r.status_code < 300)
        except AssertionError as e:
            raise type(e)(str(e) + "\n\n Full response:\n" + r.text)

    def test_post_json_no_auth_schema_neg(self):
        """
        Negative test for incorrect schema
        """
        payload = {"NOT_ID": "test"}

        r = requests.post(
            "https://europe-west1-"
            + self._domain
            + ".cloudfunctions.net/"
            + self._domain
            + "-receive-ingest-func/store-json",
            json=payload,
        )
        try:
            self.assertFalse(199 < r.status_code < 300)
        except AssertionError as e:
            raise type(e)(str(e) + "\n\n Full response:\n" + r.text)

    def test_post_json_no_auth_data_type_neg(self):
        """
        Negative test which expects store-json to not accept xml
        """
        payload = "test"
        headers = {"Content-type": "text/xml"}

        r = requests.post(
            "https://europe-west1-"
            + self._domain
            + ".cloudfunctions.net/"
            + self._domain
            + "-receive-ingest-func/store-json",
            data=payload,
            headers=headers,
        )

        try:
            self.assertFalse(199 < r.status_code < 300)
        except AssertionError as e:
            raise type(e)(str(e) + "\n\n Full response:\n" + r.text)

    def test_post_xml_no_auth_generic_pos(self):
        """
        Positive test with basic config
        """
        payload = "<?xml version='1.0' encoding='utf-8'?><test attr1='attr1'>0</test>"
        headers = {"Content-type": "application/xml"}

        r = requests.post(
            "https://europe-west1-"
            + self._domain
            + ".cloudfunctions.net/"
            + self._domain
            + "-receive-ingest-func/store-xml",
            data=payload,
            headers=headers,
        )

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
        r = requests.post(
            "https://europe-west1-"
            + self._domain
            + ".cloudfunctions.net/"
            + self._domain
            + "-receive-ingest-func/store-xml",
            data=payload,
            headers=headers,
        )

        try:
            self.assertFalse(199 < r.status_code < 300)
        except AssertionError as e:
            raise type(e)(str(e) + "\n\n Full response:\n" + r.text)

    def test_post_json_oauth_generic_pos(self):
        """
        Positive test which posts json using oauth
        """

        oauth_data = {
            "client_id": config.OAUTH_CLIENT_ID,
            "scope": config.OAUTH_EXPECTED_AUDIENCE + "/.default",
            "client_secret": secret,
            "grant_type": "client_credentials",
        }
        token = requests.post(config.OAUTH_TOKEN_URL, data=oauth_data)
        token_data = token.json()

        headers = {
            "Authorization": "Bearer " + token_data["access_token"],
            "Content-Type": "application/json",
        }

        payload = {"ID": 1}

        r = requests.post(
            "https://europe-west1-"
            + self._domain
            + ".cloudfunctions.net/"
            + self._domain
            + "-receive-ingest-func/store-json-oauth",
            headers=headers,
            data=json.dumps(payload),
        )

        try:
            self.assertTrue(199 < r.status_code < 300)
        except AssertionError as e:
            raise type(e)(str(e) + "\n\n Full response:\n" + r.text)

    def test_post_json_oauth_token_neg(self):
        """
        Negative test which posts json using oauth with an invalid token
        """
        headers = {"Authorization": "Bearer ksjjfdisj09jf912m1092m19"}

        payload = {"ID": 1}

        r = requests.post(
            "https://europe-west1-"
            + self._domain
            + ".cloudfunctions.net/"
            + self._domain
            + "-receive-ingest-func/store-json-oauth",
            headers=headers,
            json=payload,
        )

        try:
            self.assertFalse(199 < r.status_code < 300)
        except AssertionError as e:
            raise type(e)(str(e) + "\n\n Full response:\n" + r.text)
