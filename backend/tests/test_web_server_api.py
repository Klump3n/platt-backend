#!/usr/bin/env python3
"""
Test the web_server_api

"""
import unittest
from unittest import mock
import json
import pathlib
import cherrypy

# Append the parent directory for importing the file.
import sys
import os
sys.path.append(os.path.join('..', '..'))  # Append the program root dir
import backend.web_server_api
import backend.global_settings


class Test_web_server_api(unittest.TestCase):
    """
    Test the API.

    """
    def setUp(self):
        # Init the backend class
        self.api = backend.web_server_api.ServerAPI()

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

        # Initialize the global settings
        file_path = os.path.dirname(__file__)
        self.data_dir_string = 'mock_data'
        self.data_dir_path = pathlib.Path('{}/{}'.format(
            file_path, self.data_dir_string))
        backend.global_settings.init(data_dir=self.data_dir_path)

    def test_version(self):
        """Return a json string with the version

        """
        mock_dict_to_return = {
            'version': 'dict',
            'with': 'some_entries'
        }
        # The function will dump a string
        expected_string = json.dumps(mock_dict_to_return)

        # Mock the version function call
        with mock.patch(
                'util.version.version',
                return_value=mock_dict_to_return
        ) as mock_version:

            res = self.api.version()

            mock_version.assert_called()

            # Returns a string
            self.assertIsInstance(res, str)
            self.assertEqual(res, expected_string)

    def test_datasets(self):
        """Return a json string containing all datasets on the server

        """
        available_datasets = {
            'availableDatasets': ['one', 'two', 'three']
        }
        expected_string = json.dumps(available_datasets)

        with mock.patch(
                'backend.global_settings.SceneManager.list_available_datasets',
                return_value=available_datasets
        ) as mock_list_datasets:

            res = self.api.datasets()

            mock_list_datasets.assert_called()

            # Returns a string
            self.assertIsInstance(res, str)
            self.assertEqual(res, expected_string)

    def test_scenes(self):
        """Redirect to other functions based upon what we want to do

        Each choice is tested in the respective method call.

        """
        pass

    def test_get_scenes(self):
        """Return a json string containing all active scenes on the server

        """
        active_scenes = {
            'activeScenes': ['one', 'two', 'three']
        }

        with mock.patch(
                'backend.global_settings.SceneManager.list_scenes',
                return_value=active_scenes
        ) as mock_active_scenes:

            res = self.api.get_scenes()

            mock_active_scenes.assert_called()

            self.assertIsInstance(res, dict)
            self.assertEqual(res, active_scenes)

        ##################################################

        mock_cp_req = mock.MagicMock(
            cherrypy.request,
            method='GET'
        )

        expected_str = json.dumps(active_scenes)

        with mock.patch(
                'cherrypy.request',
                mock_cp_req
        ):
            with mock.patch(
                    'backend.web_server_api.ServerAPI.get_scenes',
                    return_value=active_scenes
            ) as mock_get_scenes:

                res = self.api.scenes()

                self.assertIsInstance(res, str)
                self.assertEqual(res, expected_str)

                mock_get_scenes.assert_called()

    def test_post_scenes(self):
        """Return a JSON string with a scene and objects that were created

        """
        request_dict = {
            "datasetsToAdd": [
                "numsim.napf.tiefziehversuch"
            ]
        }
        success_dict = {
            "sceneHash": "47e9f7fc6d1522c552fffaf1803a0e1822620024",
            "href": "/scenes/47e9f7fc6d1522c552fffaf1803a0e1822620024",
            "addDatasetsSuccess": [
                {
                    "datasetName": "numsim.napf.tiefziehversuch",
                    "datasetHash": "47e9f7fc6d1522c552fffaf1803a0e1822620024",
                    "datasetAlias": "",
                    "datasetHref": ""
                }
            ]
        }

        # Test self.post_scenes
        ##################################################

        with mock.patch(
                'backend.global_settings.SceneManager.new_scene',
                return_value=success_dict
        ) as mock_new_scene:

            res = self.api.post_scenes(request_dict['datasetsToAdd'])

            mock_new_scene.assert_called()

            self.assertIsInstance(res, dict)
            self.assertEqual(res, success_dict)

        # Test self.scenes, calling self.post_scenes
        ##################################################
        ##################################################

        # Expected JSON input
        ##################################################
        mock_cp_req = mock.MagicMock(
            cherrypy.request,
            method='POST',
            json=request_dict   # NOTE: does this make sense??
        )

        expected_str = json.dumps(success_dict)

        with mock.patch(
                'cherrypy.request',
                mock_cp_req
        ):
            with mock.patch(
                    'backend.web_server_api.ServerAPI.post_scenes',
                    return_value=success_dict
            ) as mock_post_scenes:

                res = self.api.scenes()

                self.assertIsInstance(res, str)
                self.assertEqual(res, expected_str)

                mock_post_scenes.assert_called()

        # Wrong request dict
        ##################################################

        wrong_request_dict = {
            "wrong_key": [
                "numsim.napf.tiefziehversuch"
            ]
        }
        mock_cp_req = mock.MagicMock(
            cherrypy.request,
            method='POST',
            json=wrong_request_dict
        )

        with mock.patch(
                'cherrypy.request',
                mock_cp_req
        ):

            res = self.api.scenes()

            self.assertIsInstance(res, str)
            self.assertEqual(res, 'null')


        # Malformed JSON input
        ##################################################

        mock_cp_req = mock.MagicMock(
            cherrypy.request,
            method='POST',
            json=json.dumps(request_dict)  # is str
        )

        expected_str = json.dumps(success_dict)

        with mock.patch(
                'cherrypy.request',
                mock_cp_req
        ):
            res = self.api.scenes()

            self.assertIsInstance(res, str)
            self.assertEqual(res, 'null')


if __name__ == '__main__':
    unittest.main(verbosity=2)
