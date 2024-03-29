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

    def test_get_scenes_scenehash(self):
        """Get a list of datasets in a scenes

        """
        scene_hash = '21dfb0dbf1034ff897aebfa0b8058a51e4a23f7a'
        expected_dict = {
            "loadedDatasets": [
                {
                    "datasetName": "numsim.napf.tiefziehversuch",
                    "datasetHash": "47e9f7fc6d1522c552fffaf1803a0e1822620024",
                    "datasetAlias": "alias for numsim.napf.tiefziehversuch",
                    "datasetHref": "/scenes/21dfb0dbf1034ff897aebfa0b8058a51e4a23f7a/47e9f7fc6d1522c552fffaf1803a0e182262002"
                }
            ]
        }

        with mock.patch(
                'backend.global_settings.SceneManager.list_loaded_datasets',
                return_value=expected_dict
        ) as mock_scenes_scenehash:

            res = self.api.get_scenes_scenehash(scene_hash)

            mock_scenes_scenehash.assert_called_with(scene_hash)

            self.assertIsInstance(res, dict)
            self.assertEqual(res, expected_dict)

        # Test self.scenes, calling self.get_scenes_scenehash
        ##################################################

        mock_cp_req = mock.MagicMock(
            cherrypy.request,
            method='GET'
        )

        expected_str = json.dumps(expected_dict)

        with mock.patch(
                'cherrypy.request',
                mock_cp_req
        ):
            with mock.patch(
                    'backend.web_server_api.ServerAPI.get_scenes_scenehash',
                    return_value=expected_dict
            ) as mock_post_scenes:

                # Call with argument
                res = self.api.scenes(scene_hash)

                self.assertIsInstance(res, str)
                self.assertEqual(res, expected_str)

                mock_post_scenes.assert_called_with(scene_hash)

    def test_post_scenes_scenehash(self):
        """Add a list of objects to a sceneHash

        """
        request_dict = {
            "datasetsToAdd": [
                "numsim.napf.tiefziehversuch"
            ]
        }
        scene_hash = '47e9f7fc6d1522c552fffaf1803a0e1822620024'
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

        # Test self.post_scenes_scenehash
        ##################################################

        with mock.patch(
                'backend.global_settings.SceneManager.add_datasets',
                return_value=success_dict
        ) as mock_add_datasets:

            res = self.api.post_scenes_scenehash(
                scene_hash, request_dict['datasetsToAdd'])

            mock_add_datasets.assert_called()

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
            json=request_dict
        )

        expected_str = json.dumps(success_dict)

        with mock.patch(
                'cherrypy.request',
                mock_cp_req
        ):
            with mock.patch(
                    'backend.web_server_api.ServerAPI.post_scenes_scenehash',
                    return_value=success_dict
            ) as mock_post_scenes:

                res = self.api.scenes(scene_hash)

                self.assertIsInstance(res, str)
                self.assertEqual(res, expected_str)

                mock_post_scenes.assert_called_with(
                    scene_hash, request_dict['datasetsToAdd'])

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

            res = self.api.scenes(scene_hash)

            self.assertIsInstance(res, str)
            self.assertEqual(res, 'null')


        # Malformed JSON input
        ##################################################

        mock_cp_req = mock.MagicMock(
            cherrypy.request,
            method='POST',
            json=json.dumps(request_dict)  # is str
        )

        with mock.patch(
                'cherrypy.request',
                mock_cp_req
        ):
            res = self.api.scenes(scene_hash)

            self.assertIsInstance(res, str)
            self.assertEqual(res, 'null')

    def test_delete_scenes_scenehash(self):
        """Delete a scene

        """
        scene_hash = '47e9f7fc6d1522c552fffaf1803a0e1822620024'
        delete_dict = {
            'sceneDeleted': scene_hash,
            'href': '/scenes'
        }

        # Test self.delete_scenes_scenehash
        ##################################################

        with mock.patch(
                'backend.global_settings.SceneManager.delete_scene',
                return_value=delete_dict
        ) as mock_delete_scene:

            res = self.api.delete_scenes_scenehash(scene_hash)

            mock_delete_scene.assert_called()

            self.assertIsInstance(res, dict)
            self.assertEqual(res, delete_dict)

        # Test self.scenes, calling self.delete_scenes_scenehash
        ##################################################

        mock_cp_req = mock.MagicMock(
            cherrypy.request,
            method='DELETE'
        )

        expected_str = json.dumps(delete_dict)

        with mock.patch(
                'cherrypy.request',
                mock_cp_req
        ):
            with mock.patch(
                    'backend.web_server_api.ServerAPI.delete_scenes_scenehash',
                    return_value=delete_dict
            ) as mock_post_scenes:

                res = self.api.scenes(scene_hash)

                self.assertIsInstance(res, str)
                self.assertEqual(res, expected_str)

                mock_post_scenes.assert_called_with(
                    scene_hash)

            # scene does not exist
            with mock.patch(
                    'backend.web_server_api.ServerAPI.delete_scenes_scenehash',
                    return_value=None
            ) as mock_post_scenes:

                res = self.api.scenes(scene_hash)

                self.assertIsInstance(res, str)
                self.assertEqual(res, 'null')

                mock_post_scenes.assert_called_with(
                    scene_hash)

    def test_get_scenes_scenehash_datasethash(self):
        """Get information about a dataset that is loaded into a scene

        """
        scene_hash = '21dfb0dbf1034ff897aebfa0b8058a51e4a23f7a'
        dataset_hash = '47e9f7fc6d1522c552fffaf1803a0e1822620024'
        expected_dict = {
            "datasetName": "numsim.napf.tiefziehversuch",
            "datasetHash": "47e9f7fc6d1522c552fffaf1803a0e1822620024",
            "datasetAlias": "alias for numsim.napf.tiefziehversuch",
            "datasetHref": "/scenes/21dfb0dbf1034ff897aebfa0b8058a51e4a23f7a/47e9f7fc6d1522c552fffaf1803a0e182262002"
        }

        # Test self.get_dataset_scenes_scenehash_datasethash
        ##################################################

        with mock.patch(
                'backend.global_settings.SceneManager.list_loaded_dataset_info',
                return_value=expected_dict
        ) as mock_get_dataset_info:

            res = self.api.get_dataset_scenes_scenehash_datasethash(scene_hash, dataset_hash)

            mock_get_dataset_info.assert_called()

            self.assertIsInstance(res, dict)
            self.assertEqual(res, expected_dict)

        # Test self.scenes, calling self.get_dataset_scenes_scenehash_datasethash
        ##################################################

        mock_cp_req = mock.MagicMock(
            cherrypy.request,
            method='GET'
        )

        expected_str = json.dumps(expected_dict)

        with mock.patch(
                'cherrypy.request',
                mock_cp_req
        ):
            with mock.patch(
                    'backend.web_server_api.ServerAPI.get_dataset_scenes_scenehash_datasethash',
                    return_value=expected_dict
            ) as mock_get_dataset_info_one:

                res = self.api.scenes(scene_hash, dataset_hash)

                self.assertIsInstance(res, str)
                self.assertEqual(res, expected_str)

                mock_get_dataset_info_one.assert_called_with(
                    scene_hash, dataset_hash)

            # scene or dataset does not exist
            with mock.patch(
                    'backend.web_server_api.ServerAPI.get_dataset_scenes_scenehash_datasethash',
                    return_value=None
            ) as mock_get_dataset_info_two:

                res = self.api.scenes(scene_hash, dataset_hash)

                self.assertIsInstance(res, str)
                self.assertEqual(res, 'null')

                mock_get_dataset_info_two.assert_called_with(
                    scene_hash, dataset_hash)

    def test_delete_scenes_scenehash_datasethash(self):
        """Delete a dataset from a scene

        """
        scene_hash = '21dfb0dbf1034ff897aebfa0b8058a51e4a23f7a'
        dataset_hash = '47e9f7fc6d1522c552fffaf1803a0e1822620024'
        expected_dict = {
            "datasetDeleted": "47e9f7fc6d1522c552fffaf1803a0e1822620024",
            "href": "/scenes/21dfb0dbf1034ff897aebfa0b8058a51e4a23f7a"
        }

        # Test self.delete_dataset_scenes_scenehash_datasethash
        ##################################################

        with mock.patch(
                'backend.global_settings.SceneManager.delete_loaded_dataset',
                return_value=expected_dict
        ) as mock_delete_dataset_info:

            res = self.api.delete_dataset_scenes_scenehash_datasethash(scene_hash, dataset_hash)

            mock_delete_dataset_info.assert_called()

            self.assertIsInstance(res, dict)
            self.assertEqual(res, expected_dict)

        # Test self.scenes, calling self.delete_dataset_scenes_scenehash_datasethash
        ##################################################

        mock_cp_req = mock.MagicMock(
            cherrypy.request,
            method='DELETE'
        )

        expected_str = json.dumps(expected_dict)

        with mock.patch(
                'cherrypy.request',
                mock_cp_req
        ):
            with mock.patch(
                    'backend.web_server_api.ServerAPI.delete_dataset_scenes_scenehash_datasethash',
                    return_value=expected_dict
            ) as mock_get_dataset_info_one:

                res = self.api.scenes(scene_hash, dataset_hash)

                self.assertIsInstance(res, str)
                self.assertEqual(res, expected_str)

                mock_get_dataset_info_one.assert_called_with(
                    scene_hash, dataset_hash)

            # scene or dataset does not exist
            with mock.patch(
                    'backend.web_server_api.ServerAPI.delete_dataset_scenes_scenehash_datasethash',
                    return_value=None
            ) as mock_get_dataset_info_two:

                res = self.api.scenes(scene_hash, dataset_hash)

                self.assertIsInstance(res, str)
                self.assertEqual(res, 'null')

                mock_get_dataset_info_two.assert_called_with(
                    scene_hash, dataset_hash)

    def test_get_scenes_scenehash_datasethash_orientation(self):
        """Get the orientation of a dataset

        """
        scene_hash = '21dfb0dbf1034ff897aebfa0b8058a51e4a23f7a'
        dataset_hash = '47e9f7fc6d1522c552fffaf1803a0e1822620024'
        expected_dict = {
            "datasetMeta": {
                "datasetName": "numsim.napf.tiefziehversuch",
                "datasetHash": "47e9f7fc6d1522c552fffaf1803a0e1822620024",
                "datasetAlias": "alias for numsim.napf.tiefziehversuch",
                "datasetHref": "/scenes/21dfb0dbf1034ff897aebfa0b8058a51e4a23f7a/47e9f7fc6d1522c552fffaf1803a0e182262002"
            },
            "datasetOrientation": [
                0.618801857889,
                0.0962469609039,
                0.282335580515,
                0.480548538153,
                0.516858801051,
                0.912111011462,
                0.865715417578,
                0.243929876095,
                0.425314633968,
                0.567040145201,
                0.482427207043,
                0.850746627011,
                0.952173194961,
                0.418593580312,
                0.491999373066,
                0.794117627953
            ]
        }
        # Test self.get_scenes_scenehash_datasethash_orientation
        ##################################################

        with mock.patch(
                'backend.global_settings.SceneManager.dataset_orientation',
                return_value=expected_dict
        ) as mock_get_orientation:

            res = self.api.get_scenes_scenehash_datasethash_orientation(scene_hash, dataset_hash)

            mock_get_orientation.assert_called()

            self.assertIsInstance(res, dict)
            self.assertEqual(res, expected_dict)

        # Test self.scenes, calling self.get_scenes_scenehash_datasethash_orientation
        ##################################################

        mock_cp_req = mock.MagicMock(
            cherrypy.request,
            method='GET'
        )

        expected_str = json.dumps(expected_dict)

        with mock.patch(
                'cherrypy.request',
                mock_cp_req
        ):
            with mock.patch(
                    'backend.web_server_api.ServerAPI.get_scenes_scenehash_datasethash_orientation',
                    return_value=expected_dict
            ) as mock_get_orientation_one:

                res = self.api.scenes(scene_hash, dataset_hash, 'orientation')

                self.assertIsInstance(res, str)
                self.assertEqual(res, expected_str)

                mock_get_orientation_one.assert_called_with(
                    scene_hash, dataset_hash)

            # scene or dataset does not exist
            with mock.patch(
                    'backend.web_server_api.ServerAPI.get_scenes_scenehash_datasethash_orientation',
                    return_value=None
            ) as mock_get_orientation_two:

                res = self.api.scenes(scene_hash, dataset_hash, 'orientation')

                self.assertIsInstance(res, str)
                self.assertEqual(res, 'null')

                mock_get_orientation_two.assert_called_with(
                    scene_hash, dataset_hash)

    def test_patch_scenes_scenehash_datasethash_orientation(self):
        """Patch the orientation of a dataset

        """
        scene_hash = '21dfb0dbf1034ff897aebfa0b8058a51e4a23f7a'
        dataset_hash = '47e9f7fc6d1522c552fffaf1803a0e1822620024'
        request_dict = {
            "datasetOrientation": [
                0.618801857889,
                0.0962469609039,
                0.282335580515,
                0.480548538153,
                0.516858801051,
                0.912111011462,
                0.865715417578,
                0.243929876095,
                0.425314633968,
                0.567040145201,
                0.482427207043,
                0.850746627011,
                0.952173194961,
                0.418593580312,
                0.491999373066,
                0.794117627953
            ]
        }
        expected_dict = {
            "datasetMeta": {
                "datasetName": "numsim.napf.tiefziehversuch",
                "datasetHash": "47e9f7fc6d1522c552fffaf1803a0e1822620024",
                "datasetAlias": "alias for numsim.napf.tiefziehversuch",
                "datasetHref": "/scenes/21dfb0dbf1034ff897aebfa0b8058a51e4a23f7a/47e9f7fc6d1522c552fffaf1803a0e182262002"
            },
            "datasetOrientation": [
                0.618801857889,
                0.0962469609039,
                0.282335580515,
                0.480548538153,
                0.516858801051,
                0.912111011462,
                0.865715417578,
                0.243929876095,
                0.425314633968,
                0.567040145201,
                0.482427207043,
                0.850746627011,
                0.952173194961,
                0.418593580312,
                0.491999373066,
                0.794117627953
            ]
        }

        # Test self.patch_scenes_scenehash_datasethash_orientation
        ##################################################

        with mock.patch(
                'backend.global_settings.SceneManager.dataset_orientation',
                return_value=expected_dict
        ) as mock_patch_orientation:

            new_or = request_dict['datasetOrientation']
            res = self.api.patch_scenes_scenehash_datasethash_orientation(scene_hash, dataset_hash, new_orientation=new_or)

            mock_patch_orientation.assert_called()

            self.assertIsInstance(res, dict)
            self.assertEqual(res, expected_dict)

        # Test self.scenes, calling self.patch_scenes_scenehash_datasethash_orientation
        ##################################################

        # Expected JSON input
        ##################################################
        mock_cp_req = mock.MagicMock(
            cherrypy.request,
            method='PATCH',
            json=request_dict
        )

        expected_str = json.dumps(expected_dict)

        with mock.patch(
                'cherrypy.request',
                mock_cp_req
        ):
            with mock.patch(
                    'backend.web_server_api.ServerAPI.patch_scenes_scenehash_datasethash_orientation',
                    return_value=expected_dict
            ) as mock_patch_orientation_one:

                res = self.api.scenes(scene_hash, dataset_hash, 'orientation')

                self.assertIsInstance(res, str)
                self.assertEqual(res, expected_str)

                new_or = request_dict['datasetOrientation']
                mock_patch_orientation_one.assert_called_with(
                    scene_hash, dataset_hash, new_orientation=new_or)

            # scene or dataset does not exist
            with mock.patch(
                    'backend.web_server_api.ServerAPI.patch_scenes_scenehash_datasethash_orientation',
                    return_value=None
            ) as mock_patch_orientation_two:

                res = self.api.scenes(scene_hash, dataset_hash, 'orientation')

                self.assertIsInstance(res, str)
                self.assertEqual(res, 'null')

                new_or = request_dict['datasetOrientation']
                mock_patch_orientation_two.assert_called_with(
                    scene_hash, dataset_hash, new_orientation=new_or)

        # Wrong request dict
        ##################################################

        wrong_request_dict = {
            "wrong_key": [
                "numsim.napf.tiefziehversuch"
            ]
        }
        mock_cp_req = mock.MagicMock(
            cherrypy.request,
            method='PATCH',
            json=wrong_request_dict
        )

        with mock.patch(
                'cherrypy.request',
                mock_cp_req
        ):

            res = self.api.scenes(scene_hash, dataset_hash, 'orientation')

            self.assertIsInstance(res, str)
            self.assertEqual(res, 'null')


        # Malformed JSON input
        ##################################################

        mock_cp_req = mock.MagicMock(
            cherrypy.request,
            method='PATCH',
            json=json.dumps(request_dict)  # is str
        )

        expected_str = json.dumps(request_dict)

        with mock.patch(
                'cherrypy.request',
                mock_cp_req
        ):
            res = self.api.scenes(scene_hash, dataset_hash, 'orientation')

            self.assertIsInstance(res, str)
            self.assertEqual(res, 'null')


    def test_get_scenes_scenehash_datasethash_timesteps(self):
        """Get the timestep of a dataset

        """
        scene_hash = '21dfb0dbf1034ff897aebfa0b8058a51e4a23f7a'
        dataset_hash = '47e9f7fc6d1522c552fffaf1803a0e1822620024'
        expected_dict = {
            "datasetMeta": {
                "datasetName": "numsim.napf.tiefziehversuch",
                "datasetHash": "47e9f7fc6d1522c552fffaf1803a0e1822620024",
                "datasetAlias": "alias for numsim.napf.tiefziehversuch",
                "datasetHref": "/scenes/21dfb0dbf1034ff897aebfa0b8058a51e4a23f7a/47e9f7fc6d1522c552fffaf1803a0e182262002"
            },
            "datasetTimestepList": [
                "000.00",
                "000.01",
                "000.02"
            ],
            "datasetTimestepSelected": "000.02"
        }

        # Test self.get_scenes_scenehash_datasethash_timesteps
        ##################################################

        with mock.patch(
                'backend.global_settings.SceneManager.dataset_timesteps',
                return_value=expected_dict
        ) as mock_get_timestep:

            res = self.api.get_scenes_scenehash_datasethash_timesteps(scene_hash, dataset_hash)

            mock_get_timestep.assert_called()

            self.assertIsInstance(res, dict)
            self.assertEqual(res, expected_dict)

        # Test self.scenes, calling self.get_scenes_scenehash_datasethash_timesteps
        ##################################################

        mock_cp_req = mock.MagicMock(
            cherrypy.request,
            method='GET'
        )

        expected_str = json.dumps(expected_dict)

        with mock.patch(
                'cherrypy.request',
                mock_cp_req
        ):
            with mock.patch(
                    'backend.web_server_api.ServerAPI.get_scenes_scenehash_datasethash_timesteps',
                    return_value=expected_dict
            ) as mock_get_timestep_one:

                res = self.api.scenes(scene_hash, dataset_hash, 'timesteps')

                self.assertIsInstance(res, str)
                self.assertEqual(res, expected_str)

                mock_get_timestep_one.assert_called_with(
                    scene_hash, dataset_hash)

            # scene or dataset does not exist
            with mock.patch(
                    'backend.web_server_api.ServerAPI.get_scenes_scenehash_datasethash_timesteps',
                    return_value=None
            ) as mock_get_timestep_two:

                res = self.api.scenes(scene_hash, dataset_hash, 'timesteps')

                self.assertIsInstance(res, str)
                self.assertEqual(res, 'null')

                mock_get_timestep_two.assert_called_with(
                    scene_hash, dataset_hash)

    def test_patch_scenes_scenehash_datasethash_timesteps(self):
        """Patch the timestep of a dataset

        """
        scene_hash = '21dfb0dbf1034ff897aebfa0b8058a51e4a23f7a'
        dataset_hash = '47e9f7fc6d1522c552fffaf1803a0e1822620024'
        request_dict = {
            "datasetTimestepSelected": "000.02"
        }
        expected_dict = {
            "datasetMeta": {
                "datasetName": "numsim.napf.tiefziehversuch",
                "datasetHash": "47e9f7fc6d1522c552fffaf1803a0e1822620024",
                "datasetAlias": "alias for numsim.napf.tiefziehversuch",
                "datasetHref": "/scenes/21dfb0dbf1034ff897aebfa0b8058a51e4a23f7a/47e9f7fc6d1522c552fffaf1803a0e182262002"
            },
            "datasetTimestepList": [
                "000.00",
                "000.01",
                "000.02"
            ],
            "datasetTimestepSelected": "000.02"
        }

        # Test self.patch_scenes_scenehash_datasethash_timesteps
        ##################################################

        with mock.patch(
                'backend.global_settings.SceneManager.dataset_timesteps',
                return_value=expected_dict
        ) as mock_patch_timestep:

            new_or = request_dict['datasetTimestepSelected']
            res = self.api.patch_scenes_scenehash_datasethash_timesteps(scene_hash, dataset_hash, new_timestep=new_or)

            mock_patch_timestep.assert_called()

            self.assertIsInstance(res, dict)
            self.assertEqual(res, expected_dict)

        # Test self.scenes, calling self.patch_scenes_scenehash_datasethash_timesteps
        ##################################################

        # Expected JSON input
        ##################################################
        mock_cp_req = mock.MagicMock(
            cherrypy.request,
            method='PATCH',
            json=request_dict
        )

        expected_str = json.dumps(expected_dict)

        with mock.patch(
                'cherrypy.request',
                mock_cp_req
        ):
            with mock.patch(
                    'backend.web_server_api.ServerAPI.patch_scenes_scenehash_datasethash_timesteps',
                    return_value=expected_dict
            ) as mock_patch_timestep_one:

                res = self.api.scenes(scene_hash, dataset_hash, 'timesteps')

                self.assertIsInstance(res, str)
                self.assertEqual(res, expected_str)

                new_or = request_dict['datasetTimestepSelected']
                mock_patch_timestep_one.assert_called_with(
                    scene_hash, dataset_hash, new_timestep=new_or)

            # scene or dataset does not exist
            with mock.patch(
                    'backend.web_server_api.ServerAPI.patch_scenes_scenehash_datasethash_timesteps',
                    return_value=None
            ) as mock_patch_timestep_two:

                res = self.api.scenes(scene_hash, dataset_hash, 'timesteps')

                self.assertIsInstance(res, str)
                self.assertEqual(res, 'null')

                new_or = request_dict['datasetTimestepSelected']
                mock_patch_timestep_two.assert_called_with(
                    scene_hash, dataset_hash, new_timestep=new_or)

        # Wrong request dict
        ##################################################

        wrong_request_dict = {
            "wrong_key": [
                "numsim.napf.tiefziehversuch"
            ]
        }
        mock_cp_req = mock.MagicMock(
            cherrypy.request,
            method='PATCH',
            json=wrong_request_dict
        )

        with mock.patch(
                'cherrypy.request',
                mock_cp_req
        ):

            res = self.api.scenes(scene_hash, dataset_hash, 'timesteps')

            self.assertIsInstance(res, str)
            self.assertEqual(res, 'null')


        # Malformed JSON input
        ##################################################

        mock_cp_req = mock.MagicMock(
            cherrypy.request,
            method='PATCH',
            json=json.dumps(request_dict)  # is str
        )

        expected_str = json.dumps(request_dict)

        with mock.patch(
                'cherrypy.request',
                mock_cp_req
        ):
            res = self.api.scenes(scene_hash, dataset_hash, 'timesteps')

            self.assertIsInstance(res, str)
            self.assertEqual(res, 'null')


    def test_get_scenes_scenehash_datasethash_fields(self):
        """Get the field of a dataset

        """
        scene_hash = '21dfb0dbf1034ff897aebfa0b8058a51e4a23f7a'
        dataset_hash = '47e9f7fc6d1522c552fffaf1803a0e1822620024'
        expected_dict = {
            "datasetMeta": {
                "datasetName": "numsim.napf.tiefziehversuch",
                "datasetHash": "47e9f7fc6d1522c552fffaf1803a0e1822620024",
                "datasetAlias": "alias for numsim.napf.tiefziehversuch",
                "datasetHref": "/scenes/21dfb0dbf1034ff897aebfa0b8058a51e4a23f7a/47e9f7fc6d1522c552fffaf1803a0e182262002"
            },
            "datasetFieldList": {
                "elemental": [
                    "elemental_field_1",
                    "elemental_field_2"
                ],
                "nodal": [
                    "nodal_field_1",
                    "nodal_field_2"
                ]
            },
            "datasetFieldSelected": "nodal_field_2"
        }
        # Test self.get_scenes_scenehash_datasethash_fields
        ##################################################

        with mock.patch(
                'backend.global_settings.SceneManager.dataset_fields',
                return_value=expected_dict
        ) as mock_get_field:

            res = self.api.get_scenes_scenehash_datasethash_fields(scene_hash, dataset_hash)

            mock_get_field.assert_called()

            self.assertIsInstance(res, dict)
            self.assertEqual(res, expected_dict)

        # Test self.scenes, calling self.get_scenes_scenehash_datasethash_fields
        ##################################################

        mock_cp_req = mock.MagicMock(
            cherrypy.request,
            method='GET'
        )

        expected_str = json.dumps(expected_dict)

        with mock.patch(
                'cherrypy.request',
                mock_cp_req
        ):
            with mock.patch(
                    'backend.web_server_api.ServerAPI.get_scenes_scenehash_datasethash_fields',
                    return_value=expected_dict
            ) as mock_get_field_one:

                res = self.api.scenes(scene_hash, dataset_hash, 'fields')

                self.assertIsInstance(res, str)
                self.assertEqual(res, expected_str)

                mock_get_field_one.assert_called_with(
                    scene_hash, dataset_hash)

            # scene or dataset does not exist
            with mock.patch(
                    'backend.web_server_api.ServerAPI.get_scenes_scenehash_datasethash_fields',
                    return_value=None
            ) as mock_get_field_two:

                res = self.api.scenes(scene_hash, dataset_hash, 'fields')

                self.assertIsInstance(res, str)
                self.assertEqual(res, 'null')

                mock_get_field_two.assert_called_with(
                    scene_hash, dataset_hash)

    def test_patch_scenes_scenehash_datasethash_fields(self):
        """Patch the field of a dataset

        """
        scene_hash = '21dfb0dbf1034ff897aebfa0b8058a51e4a23f7a'
        dataset_hash = '47e9f7fc6d1522c552fffaf1803a0e1822620024'
        request_dict = {
            "datasetFieldSelected": "nodal_field_2"
        }
        expected_dict = {
            "datasetMeta": {
                "datasetName": "numsim.napf.tiefziehversuch",
                "datasetHash": "47e9f7fc6d1522c552fffaf1803a0e1822620024",
                "datasetAlias": "alias for numsim.napf.tiefziehversuch",
                "datasetHref": "/scenes/21dfb0dbf1034ff897aebfa0b8058a51e4a23f7a/47e9f7fc6d1522c552fffaf1803a0e182262002"
            },
            "datasetFieldList": {
                "elemental": [
                    "elemental_field_1",
                    "elemental_field_2"
                ],
                "nodal": [
                    "nodal_field_1",
                    "nodal_field_2"
                ]
            },
            "datasetFieldSelected": "nodal_field_2"
        }
        # Test self.patch_scenes_scenehash_datasethash_fields
        ##################################################

        with mock.patch(
                'backend.global_settings.SceneManager.dataset_fields',
                return_value=expected_dict
        ) as mock_patch_field:

            new_or = request_dict['datasetFieldSelected']
            res = self.api.patch_scenes_scenehash_datasethash_fields(scene_hash, dataset_hash, new_field=new_or)

            mock_patch_field.assert_called()

            self.assertIsInstance(res, dict)
            self.assertEqual(res, expected_dict)

        # Test self.scenes, calling self.patch_scenes_scenehash_datasethash_fields
        ##################################################

        # Expected JSON input
        ##################################################
        mock_cp_req = mock.MagicMock(
            cherrypy.request,
            method='PATCH',
            json=request_dict
        )

        expected_str = json.dumps(expected_dict)

        with mock.patch(
                'cherrypy.request',
                mock_cp_req
        ):
            with mock.patch(
                    'backend.web_server_api.ServerAPI.patch_scenes_scenehash_datasethash_fields',
                    return_value=expected_dict
            ) as mock_patch_field_one:

                res = self.api.scenes(scene_hash, dataset_hash, 'fields')

                self.assertIsInstance(res, str)
                self.assertEqual(res, expected_str)

                new_or = request_dict['datasetFieldSelected']
                mock_patch_field_one.assert_called_with(
                    scene_hash, dataset_hash, new_field=new_or)

            # scene or dataset does not exist
            with mock.patch(
                    'backend.web_server_api.ServerAPI.patch_scenes_scenehash_datasethash_fields',
                    return_value=None
            ) as mock_patch_field_two:

                res = self.api.scenes(scene_hash, dataset_hash, 'fields')

                self.assertIsInstance(res, str)
                self.assertEqual(res, 'null')

                new_or = request_dict['datasetFieldSelected']
                mock_patch_field_two.assert_called_with(
                    scene_hash, dataset_hash, new_field=new_or)

        # Wrong request dict
        ##################################################

        wrong_request_dict = {
            "wrong_key": [
                "numsim.napf.tiefziehversuch"
            ]
        }
        mock_cp_req = mock.MagicMock(
            cherrypy.request,
            method='PATCH',
            json=wrong_request_dict
        )

        with mock.patch(
                'cherrypy.request',
                mock_cp_req
        ):

            res = self.api.scenes(scene_hash, dataset_hash, 'fields')

            self.assertIsInstance(res, str)
            self.assertEqual(res, 'null')


        # Malformed JSON input
        ##################################################

        mock_cp_req = mock.MagicMock(
            cherrypy.request,
            method='PATCH',
            json=json.dumps(request_dict)  # is str
        )

        expected_str = json.dumps(request_dict)

        with mock.patch(
                'cherrypy.request',
                mock_cp_req
        ):
            res = self.api.scenes(scene_hash, dataset_hash, 'fields')

            self.assertIsInstance(res, str)
            self.assertEqual(res, 'null')



if __name__ == '__main__':
    unittest.main(verbosity=2)
