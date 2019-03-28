# coding: utf-8

from __future__ import absolute_import
import unittest

from flask import json
from six import BytesIO

from openapi_server.models.devices_locations import DevicesLocations  # noqa: E501
from openapi_server.test import BaseTestCase


class TestDefaultController(BaseTestCase):
    """DefaultController integration test stubs"""

    def test_createdevices_location(self):
        """Test case for createdevices_location

        Create a devicesLocation
        """
        body = {}
        headers = { 
            'Content-Type': 'application/json',
        }
        response = self.client.open(
            '/devicesLocations',
            method='POST',
            headers=headers,
            data=json.dumps(body),
            content_type='application/json')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_devices_locations_get(self):
        """Test case for devices_locations_get

        
        """
        headers = { 
            'Accept': 'application/json',
        }
        response = self.client.open(
            '/devicesLocations',
            method='GET',
            headers=headers)
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))


if __name__ == '__main__':
    unittest.main()
