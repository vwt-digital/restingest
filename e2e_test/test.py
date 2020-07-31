import unittest
import requests
import sys


class E2ETest(unittest.TestCase):
    _domain = ''

    def test_sunny_day(self):
        self.assertTrue(0xDEADBEEF)

    def test_get_json_stg_store_generic(self):
        params = {
            'geturl': 'generics'
        }
        payload = {
            'geturl': 'generics'
        }
        r = requests.post(f'https://europe-west1-{self._domain}.cloudfunctions.net/'
                          f'{self._domain}-request-ingest-func', params=params, json=payload)
        print(r.text)
        print(r.content)
        try:
            self.assertTrue(199 < r.status_code < 300)
        except AssertionError as e:
            import sys
            raise type(e)(str(e) + "\n\n Full response:\n" + r.text).with_traceback(sys.exc_info()[2])

    # def test_post_json_no_auth_generic_pos(self):
    #     payload = {
    #         'ID': 0
    #     }
    #
    #     r = requests.post('https://europe-west1-vwt-d-gew1-dat-restingest-test.cloudfunctions.net/vwt-d-gew1-dat'
    #                       '-restingest-test-receive-ingest-func/store-json', json=payload)
    #     try:
    #         self.assertTrue(199 < r.status_code < 300)
    #     except AssertionError as e:
    #         raise type(e)(str(e) + "\n\n Full response:\n" + r.text)

    # def test_post_json_no_auth_generic_neg(self):
    #     r = requests.post('https://europe-west1-vwt-d-gew1-dat-restingest-test.cloudfunctions.net/vwt-d-gew1-dat'
    #                       '-restingest-test-receive-ingest-func/store-json')
    #     try:
    #         self.assertFalse(199 < r.status_code < 300)
    #     except AssertionError as e:
    #         raise type(e)(str(e) + "\n\n Full response:\n" + r.text)

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
    #         import sys
    #         raise type(e)(str(e) + "\n\n Full response:\n" + r.text).with_traceback(sys.exc_info()[2])


if __name__ == "__main__":
    if len(sys.argv) < 1:
        print('No domain arguments found')
        exit(1)
    E2ETest._domain = sys.argv.pop()
    unittest.main()
