#!/usr/bin/env python3
"""
Tests for do_datasets.

"""
import unittest
import json
import responses

import sys
import os
sys.path.append(os.path.join('..', '..', '..'))
import client._dos.do_datasets as do_datasets


class Test_do_datasets(unittest.TestCase):

    def setUp(self):
        """Set up stuff

        """
        self.host = '0.0.0.0'
        self.port = 8008
        self.program_name = 'norderney'
        self.program_version = 'alpha-21-ge897462'

        self.headers = {'user-agent': '{}/{}'.format(
            self.program_name, self.program_version)}

        self.c_data = {}
        self.c_data['host'] = self.host
        self.c_data['port'] = self.port
        self.c_data['headers'] = self.headers

        self.available_datasets = {
            "availableDatasets": [
                "just_fo",
                "another_just_fo",
                "fo_and_frb"
            ]}

    @responses.activate
    def test_list_datasets(self):
        """Get a list of datasets from the backend

        """
        # Server is online and responds correctly
        target_path_scene = 'http://{}:{}/api/{}'.format(
            self.host, self.port, 'datasets')
        with responses.RequestsMock() as rsps:
            rsps.add(
                responses.GET, target_path_scene,
                json=json.dumps(self.available_datasets), status=200
            )
            res = do_datasets.datasets(self.c_data)
            self.assertEqual(res, self.available_datasets)

        # Server is offline
        res = do_datasets.datasets(self.c_data)
        self.assertIsNone(res)

        # Returned data is malformed
        malformed_datasets = {
            "some_other_key": [
                "just_fo",
                "another_just_fo",
                "fo_and_frb"
            ]}
        with responses.RequestsMock() as rsps:
            rsps.add(
                responses.GET, target_path_scene,
                json=json.dumps(malformed_datasets), status=200
            )
            res = do_datasets.datasets(self.c_data)
            self.assertIsNone(res)


if __name__ == '__main__':
    unittest.main(verbosity=2)
