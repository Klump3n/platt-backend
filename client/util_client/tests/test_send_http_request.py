#!/usr/bin/env python3
"""
Tests for sending HTTP requests.

"""
import unittest
import json
import responses

# For local testing
import os
import sys
sys.path.append(os.path.join('..', '..', '..'))
from client.util_client.send_http_request import send_http_request


class Test_send_http_request(unittest.TestCase):
    """
    Test sending HTTP requests and processing them.

    """
    def setUp(self):
        self.host = '0.0.0.0'
        self.port = 8008
        self.program_name = 'norderney'
        self.program_version = 'alpha-21-ge897462'

        # Construct the header
        self.headers = {'user-agent': '{}/{}'.format(
            self.program_name, self.program_version)}

        # A dict with connection data for easy handing into functions
        self.c_data = {}
        self.c_data['host'] = self.host
        self.c_data['port'] = self.port
        self.c_data['headers'] = self.headers
        # self.host = '0.0.0.0'
        # self.port = 8008
        # self.headers = {
        #     "programName": "norderney",
        #     "programVersion": "alpha-21-ge897462"
        # }
        # self.c_data = {}
        # self.c_data['host'] = self.host
        # self.c_data['port'] = self.port
        # self.c_data['headers'] = self.headers

    @responses.activate
    def test_call_parameters(self):
        """Call the send_http_request function

        """
        api_endpoint = ''
        target_path = 'http://{}:{}/api/{}'.format(
            self.host, self.port, api_endpoint)
        json_file = {'proper': 'response'}

        # Assure it works
        with responses.RequestsMock() as rsps:
            rsps.add(
                responses.GET, target_path,
                json=json.dumps(json_file), status=200)

            res = send_http_request(
                http_method='GET',
                api_endpoint=api_endpoint,
                connection_data=self.c_data,
                data_to_transmit=None
            )
            self.assertEqual(res, json_file)

            rsps.add(
                responses.GET, target_path,
                json=json.dumps(json_file), status=200)

            # Accepts also dict for data_to_transmit
            data_to_transmit = {'some': 'data'}
            res = send_http_request(
                http_method='GET',
                api_endpoint=api_endpoint,
                connection_data=self.c_data,
                data_to_transmit=data_to_transmit
            )
            self.assertEqual(res, json_file)

        # All working methods
        for method in [
                # {'GET': responses.GET},  # Already tested
                {'POST': responses.POST},
                {'DELETE': responses.DELETE},
                {'PATCH': responses.PATCH}
        ]:
            key = sorted(method.keys())[0]
            value = sorted(method.values())[0]

            with responses.RequestsMock() as rsps:
                rsps.add(
                    value, target_path,
                    json=json.dumps(json_file), status=200)
                res = send_http_request(
                    http_method=key,
                    api_endpoint=api_endpoint,
                    connection_data=self.c_data,
                    data_to_transmit=None
                )
                self.assertEqual(res, json_file)

        # Wrong method type
        with self.assertRaises(TypeError):
            send_http_request(
                http_method=1,
                api_endpoint=api_endpoint,
                connection_data=self.c_data,
                data_to_transmit=None
            )

        # Unsupported HTTP method
        with self.assertRaises(ValueError):
            send_http_request(
                http_method='PUT',
                api_endpoint=api_endpoint,
                connection_data=self.c_data,
                data_to_transmit=None
            )

        # Wrong api_endpoint type
        with self.assertRaises(TypeError):
            send_http_request(
                http_method='GET',
                api_endpoint=1,
                connection_data=self.c_data,
                data_to_transmit=None
            )

        # Wrong connection data type
        with self.assertRaises(TypeError):
            send_http_request(
                http_method='GET',
                api_endpoint=api_endpoint,
                connection_data=1,
                data_to_transmit=None
            )

        # Wrong data_to_transmit type
        with self.assertRaises(TypeError):
            send_http_request(
                http_method='GET',
                api_endpoint=api_endpoint,
                connection_data=self.c_data,
                data_to_transmit='a_string'
            )

        # Malformed connection data (headers missing)
        malformed_c_data = {}
        malformed_c_data['host'] = self.host
        malformed_c_data['port'] = self.port
        with self.assertRaises(ValueError):
            send_http_request(
                http_method='GET',
                api_endpoint=api_endpoint,
                connection_data=malformed_c_data,
                data_to_transmit=None
            )

        # If the server does not return JSON the method returns None
        with responses.RequestsMock() as rsps:
            rsps.add(
                responses.GET, target_path,
                json=json_file, status=200)
            res = send_http_request(
                http_method='GET',
                api_endpoint=api_endpoint,
                connection_data=self.c_data,
                data_to_transmit=None
            )
            self.assertIsNone(res)

        # If the server does not return a 200 code the method returns nothing
        with responses.RequestsMock() as rsps:
            rsps.add(
                responses.GET, target_path,
                json=None, status=404)
            res = send_http_request(
                http_method='GET',
                api_endpoint=api_endpoint,
                connection_data=self.c_data,
                data_to_transmit=None
            )
            self.assertIsNone(res)

        # If the api endpoint does not exist the method returns None
        res = send_http_request(
            http_method='GET',
            api_endpoint='does_not_exist',
            connection_data=self.c_data,
            data_to_transmit=None
        )
        self.assertIsNone(res)

        # Server is offline and method returns None
        other_c_data = {}
        other_c_data['host'] = '10.10.10.10'
        other_c_data['port'] = 8008
        other_c_data['headers'] = self.headers
        res = send_http_request(
            http_method='GET',
            api_endpoint=api_endpoint,
            connection_data=other_c_data,
            data_to_transmit=None
        )
        self.assertIsNone(res)


if __name__ == '__main__':
    unittest.main(verbosity=2)
