#!/usr/bin/env python3
"""
Test the host_test module.

"""
import unittest
import json
import responses

# For local testing
import os
import sys
sys.path.append(os.path.join('..', '..', '..'))
from client.util_client.host_test import target_online_and_compatible


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

        self.json_return = {
            'programName': self.program_name,
            'programVersion': self.program_version
        }

    @responses.activate
    def test_host_test(self):
        """Checking if host is up/down/running a different version

        """
        # Server online and runs the right version
        target_path = 'http://{}:{}/api/version'.format(
            self.host, self.port)

        with responses.RequestsMock() as rsps:
            rsps.add(
                responses.GET, target_path,
                json=json.dumps(self.json_return), status=200
            )
            host_up_and_compatible = target_online_and_compatible(self.c_data)
            self.assertTrue(host_up_and_compatible)

        # Server offline
        host_up_and_compatible = target_online_and_compatible(self.c_data)
        self.assertFalse(host_up_and_compatible)

        # Version mismatch
        mismatched_json_return = {
            'programName': self.program_name,
            'programVersion': 'some_other_version'
        }
        target_path = 'http://{}:{}/api/version'.format(
            self.host, self.port)

        with responses.RequestsMock() as rsps:
            rsps.add(
                responses.GET, target_path,
                json=json.dumps(mismatched_json_return), status=200
            )
            host_up_and_compatible = target_online_and_compatible(self.c_data)
            self.assertFalse(host_up_and_compatible)


if __name__ == '__main__':
    unittest.main(verbosity=2)
