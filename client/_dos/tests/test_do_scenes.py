#!/usr/bin/env python3
"""
Tests for do_scenes.

"""
import unittest
import json
import responses
from unittest import mock

import sys
import os
sys.path.append(os.path.join('..', '..', '..'))
import client._dos.do_scenes as do_scenes


class Test_do_scenes(unittest.TestCase):

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

        self.active_scenes = {
            "activeScenes": [
                "babf090679cf7b50f1a52138dadc9ea50b6b0700",
                "77d8548a5def0e7a410259296eb24776ae19047c",
                "4c0e21b939da38778e76a03e284bb5ed92e6fdf7"
            ]}
        self.scene_hash = '4c0e21b939da38778e76a03e284bb5ed92e6fdf7'
        self.loaded_datasets = {
            "loadedDatasets": [
                {
                    "datasetName": "just_fo",
                    "datasetHash": "babf090679cf7b50f1a52138dadc9ea50b6b0700",
                    "datasetAlias": "alias 1",
                    "datasetHref": "/scenes/4c0e21b939da38778e76a03e284bb5ed92e6fdf7/babf090679cf7b50f1a52138dadc9ea50b6b0700"
                },
                {
                    "datasetName": "another_just_fo",
                    "datasetHash": "77d8548a5def0e7a410259296eb24776ae19047c",
                    "datasetAlias": "alias 2",
                    "datasetHref": "/scenes/4c0e21b939da38778e76a03e284bb5ed92e6fdf7/77d8548a5def0e7a410259296eb24776ae19047c"
                }
            ]
        }

    def test_clean_list(self):
        """Remove empty entries from a list

        """
        clean_list = ['a', 'b', 'c']
        dirty_list_1 = ['', 'a', 'b', 'c']
        dirty_list_2 = ['', 'a', '', 'b', 'c']
        dirty_list_3 = ['', 'a', '', 'b', 'c', '']
        dirty_list_4 = ['', '', '', 'a', '', 'b', 'c', '']

        self.assertEqual(clean_list, do_scenes.clean_list(clean_list))
        self.assertEqual(clean_list, do_scenes.clean_list(dirty_list_1))
        self.assertEqual(clean_list, do_scenes.clean_list(dirty_list_2))
        self.assertEqual(clean_list, do_scenes.clean_list(dirty_list_3))
        self.assertEqual(clean_list, do_scenes.clean_list(dirty_list_4))

        with self.assertRaises(TypeError):
            do_scenes.clean_list({1: 2})

    def test_pretty_print_scenes(self):
        """Pretty print a scene.

        """
        with mock.patch(
                'client._dos.do_scenes.send_http_request',
                return_value=self.loaded_datasets
        ) as mock_http_req:

            res = do_scenes.pretty_print_scene(self.scene_hash, self.c_data)

            mock_http_req.assert_called_with(
                http_method='GET',
                api_endpoint='scenes/4c0e21b939da38778e76a03e284bb5ed92e6fdf7',
                connection_data=self.c_data,
                data_to_transmit=None
            )

            self.assertEqual(res, self.scene_hash)

        # scene_hash can not be resolved returns None
        with mock.patch(
                'client._dos.do_scenes.send_http_request',
                return_value=None
        ) as mock_http_req:

            res = do_scenes.pretty_print_scene(self.scene_hash, self.c_data)
            self.assertIsNone(res)

        # Wrong scene_hash type
        with self.assertRaises(TypeError):
            do_scenes.pretty_print_scene(1, self.c_data)

        # Wrong c_data type
        with self.assertRaises(TypeError):
            do_scenes.pretty_print_scene(self.scene_hash, 1)

    def test_scenes_list(self):
        """Get a listing of scenes

        """
        with mock.patch(
                'client._dos.do_scenes.send_http_request',
                side_effect=[
                    self.active_scenes,
                    self.loaded_datasets,
                    self.loaded_datasets,
                    self.loaded_datasets
                ]
        ) as mock_http_req:

            res = do_scenes.scenes_list(self.c_data)
            expected_res = self.active_scenes['activeScenes']

            mock_http_req.assert_any_call(
                http_method='GET',
                api_endpoint='scenes',
                connection_data=self.c_data,
                data_to_transmit=None
            )
            mock_http_req.assert_any_call(
                http_method='GET',
                api_endpoint='scenes/babf090679cf7b50f1a52138dadc9ea50b6b0700',
                connection_data=self.c_data,
                data_to_transmit=None
            )
            mock_http_req.assert_any_call(
                http_method='GET',
                api_endpoint='scenes/77d8548a5def0e7a410259296eb24776ae19047c',
                connection_data=self.c_data,
                data_to_transmit=None
            )
            mock_http_req.assert_any_call(
                http_method='GET',
                api_endpoint='scenes/4c0e21b939da38778e76a03e284bb5ed92e6fdf7',
                connection_data=self.c_data,
                data_to_transmit=None
            )

            self.assertEqual(res, expected_res)

        # Wrong c_data type
        with self.assertRaises(TypeError):
            do_scenes.scenes_list(1)

        # Wrong just type
        with self.assertRaises(TypeError):
            do_scenes.scenes_list(self.c_data, just={})

        # # Try displaying just one scene. NOTE: 'JUST' IS NOT REALLY IMPLEMENTED YET
        # just = ['77d8548a5def0e7a410259296eb24776ae19047c']
        # with mock.patch(
        #         'client._dos.do_scenes.send_http_request',
        #         side_effect=[
        #             self.active_scenes,
        #             self.loaded_datasets
        #         ]
        # ) as mock_http_req:

        #     res = do_scenes.scenes_list(self.c_data, just=just)

        #     mock_http_req.assert_any_call(
        #         http_method='GET',
        #         api_endpoint='scenes',
        #         connection_data=self.c_data,
        #         data_to_transmit=None
        #     )
        #     mock_http_req.assert_any_call(
        #         http_method='GET',
        #         api_endpoint='scenes/77d8548a5def0e7a410259296eb24776ae19047c',
        #         connection_data=self.c_data,
        #         data_to_transmit=None
        #     )

        #     self.assertEqual(res, just)

        # # Try displaying just one scene
        # just = ['no_such_scene']
        # with mock.patch(
        #         'client._dos.do_scenes.send_http_request',
        #         return_value=self.active_scenes
        # ) as mock_http_req:

        #     res = do_scenes.scenes_list(self.c_data, just=just)

        #     mock_http_req.assert_any_call(
        #         http_method='GET',
        #         api_endpoint='scenes',
        #         connection_data=self.c_data,
        #         data_to_transmit=None
        #     )

        # # The scene we JUST want to display does not exist
        # just = ['no_such_scene']
        # target_path_scenes_just = 'http://{}:{}/api/{}'.format(
        #     self.host, self.port, 'scenes')

        # with responses.RequestsMock() as rsps:
        #     rsps.add(
        #         responses.GET, target_path_scenes_just,
        #         json=json.dumps(self.active_scenes), status=200)

        #     res = do_scenes.scenes_list(self.c_data, just=just)
        #     self.assertEqual(res, [])

        # # just is not a list but something else
        # with self.assertRaises(TypeError):
        #     do_scenes.scenes_list(self.c_data, just='not_a_list')

    def test_scenes_create(self):
        """Create a new scene

        """
        dataset_list = ['object_a', 'object_b']
        send_dict = {
            'datasetsToAdd': dataset_list
        }
        success_list = [
            {
                "datasetName": "object_b",
                "datasetHash": "47e9f7fc6d1522c552fffaf1803a0e1822620024",
                "datasetAlias": "alias for numsim.napf.tiefziehversuch",
                "datasetHref": "/scenes/21dfb0dbf1034ff897aebfa0b8058a51e4a23f7a/47e9f7fc6d1522c552fffaf1803a0e182262002"
            }
        ]
        success_dict = {
            "sceneHash": "47e9f7fc6d1522c552fffaf1803a0e1822620024",
            "href": "/scenes/47e9f7fc6d1522c552fffaf1803a0e1822620024",
            "addDatasetsSuccess": success_list
        }

        # Full success
        with mock.patch(
                'client._dos.do_scenes.send_http_request',
                return_value=success_dict
        ) as mock_http_req:

            with mock.patch(
                    'client._dos.do_scenes.pretty_print_scene',
                    return_value=None  # does not have to return anything
            ) as mock_pps:

                res = do_scenes.scenes_create(self.c_data, dataset_list)

                mock_http_req.assert_any_call(
                    http_method='POST',
                    api_endpoint='scenes',
                    connection_data=self.c_data,
                    data_to_transmit=send_dict
                )
                mock_pps.assert_any_call(
                    '47e9f7fc6d1522c552fffaf1803a0e1822620024', self.c_data
                )

                self.assertIsInstance(res, list)
                self.assertEqual(res, success_list)

        # # Partial success
        # test_later

        # No response
        with mock.patch(
                'client._dos.do_scenes.send_http_request',
                return_value=None
        ) as mock_http_req:

            res = do_scenes.scenes_create(self.c_data, dataset_list)

            mock_http_req.assert_any_call(
                http_method='POST',
                api_endpoint='scenes',
                connection_data=self.c_data,
                data_to_transmit=send_dict
            )

            self.assertIsNone(res)

        # Wrong c_data type
        with self.assertRaises(TypeError):
            do_scenes.scenes_create(dataset_list, dataset_list)

        # Wrong dataset_list type
        with self.assertRaises(TypeError):
            do_scenes.scenes_create(self.c_data, self.c_data)

    def test_scenes_delete(self):
        """Delete a scene from the backend

        """
        scene_hash = ['21dfb0dbf1034ff897aebfa0b8058a51e4a23f7a']
        expected_dict = {
            "sceneDeleted": "21dfb0dbf1034ff897aebfa0b8058a51e4a23f7a",
            "href": "/scenes"
        }

        # Working properly
        with mock.patch(
                'client._dos.do_scenes.send_http_request',
                return_value=expected_dict
        ) as mock_delete_scene:

            res = do_scenes.scenes_delete(self.c_data, scene_hash)

            mock_delete_scene.assert_called_with(
                http_method='DELETE',
                api_endpoint='scenes/21dfb0dbf1034ff897aebfa0b8058a51e4a23f7a',
                connection_data=self.c_data,
                data_to_transmit=None
            )

            self.assertEqual(res, scene_hash)

        # No response
        with mock.patch(
                'client._dos.do_scenes.send_http_request',
                return_value=None
        ) as mock_delete_scene:

            res = do_scenes.scenes_delete(self.c_data, scene_hash)

            mock_delete_scene.assert_called_with(
                http_method='DELETE',
                api_endpoint='scenes/21dfb0dbf1034ff897aebfa0b8058a51e4a23f7a',
                connection_data=self.c_data,
                data_to_transmit=None
            )

            self.assertIsNone(res)

        # Wrong argument types
        with self.assertRaises(TypeError):
            do_scenes.scenes_delete(self.c_data, 1)
        with self.assertRaises(TypeError):
            do_scenes.scenes_delete(1, scene_hash)

    def test_scenes_select(self):
        """Select a scene and open a new terminal instance

        """
        # Select a valid scene
        with mock.patch(
                'client._dos.do_scenes.send_http_request',
                return_value=self.active_scenes
        ) as mock_http_req:

            scene_hash = 'babf090679cf7b50f1a52138dadc9ea50b6b0700'

            # So we can assert that the method is getting a call
            with mock.patch(
                    'client._dos.scene_manipulation.scene_manipulation.select'
            ) as mock_select_scene:

                do_scenes.scenes_select(self.c_data, scene_hash)

                mock_http_req.assert_called_with(
                    http_method='GET',
                    api_endpoint='scenes',
                    connection_data=self.c_data,
                    data_to_transmit=None
                )

                mock_select_scene.assert_called_with(self.c_data, scene_hash)

        # Select an invalid scene
        with mock.patch(
                'client._dos.do_scenes.send_http_request',
                return_value=self.active_scenes
        ) as mock_http_req:

            scene_hash = 'invalid_scene'

            res = do_scenes.scenes_select(self.c_data, scene_hash)

            mock_http_req.assert_called_with(
                http_method='GET',
                api_endpoint='scenes',
                connection_data=self.c_data,
                data_to_transmit=None
            )

            self.assertIsNone(res)

        # invalid scene hash type returns None
        with mock.patch(
                'client._dos.do_scenes.send_http_request',
                return_value=self.active_scenes
        ) as mock_http_req:

            scene_hash = 1

            res = do_scenes.scenes_select(self.c_data, scene_hash)

            mock_http_req.assert_called_with(
                http_method='GET',
                api_endpoint='scenes',
                connection_data=self.c_data,
                data_to_transmit=None
            )

            self.assertIsNone(res)


if __name__ == '__main__':
    unittest.main(verbosity=2)
