#!/usr/bin/env python3
"""
Tests for do_scenes.

"""
import unittest
import json
import responses

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

    @responses.activate
    def test_pretty_print_scenes(self):
        """Pretty print a scene.

        """
        target_path_scene = 'http://{}:{}/api/{}'.format(
            self.host, self.port,
            'scenes/4c0e21b939da38778e76a03e284bb5ed92e6fdf7')

        with responses.RequestsMock() as rsps:
            rsps.add(
                responses.GET, target_path_scene,
                json=json.dumps(self.loaded_datasets), status=200
            )
            res = do_scenes.pretty_print_scene(self.scene_hash, self.c_data)
            self.assertEqual(res, self.scene_hash)

        # scene_hash can not be resolved returns None
        res = do_scenes.pretty_print_scene(self.scene_hash, self.c_data)
        self.assertIsNone(res)

        # Wrong scene_hash type
        with self.assertRaises(TypeError):
            do_scenes.pretty_print_scene(1, self.c_data)

        # Wrong c_data type
        with self.assertRaises(TypeError):
            do_scenes.pretty_print_scene(self.scene_hash, 1)

    @responses.activate
    def test_scenes_list(self):
        """Get a listing of scenes

        """
        target_path_scenes = 'http://{}:{}/api/{}'.format(
            self.host, self.port, 'scenes')
        target_path_scene_1 = 'http://{}:{}/api/{}'.format(
            self.host, self.port,
            'scenes/babf090679cf7b50f1a52138dadc9ea50b6b0700')
        target_path_scene_2 = 'http://{}:{}/api/{}'.format(
            self.host, self.port,
            'scenes/77d8548a5def0e7a410259296eb24776ae19047c')
        target_path_scene_3 = 'http://{}:{}/api/{}'.format(
            self.host, self.port,
            'scenes/4c0e21b939da38778e76a03e284bb5ed92e6fdf7')

        # Create a couple of mock calls that will be called one after the other
        with responses.RequestsMock() as rsps:
            rsps.add(
                responses.GET, target_path_scenes,
                json=json.dumps(self.active_scenes), status=200)
            rsps.add(
                responses.GET, target_path_scene_1,
                json=json.dumps(self.loaded_datasets), status=200)
            rsps.add(
                responses.GET, target_path_scene_2,
                json=json.dumps(self.loaded_datasets), status=200)
            rsps.add(
                responses.GET, target_path_scene_3,
                json=json.dumps(self.loaded_datasets), status=200)

            # This calls all four of the prepared mock responses
            res = do_scenes.scenes_list(self.c_data)
            expected_res = self.active_scenes['activeScenes']

            self.assertEqual(res, expected_res)

        # Try displaying just one scene
        just = ['77d8548a5def0e7a410259296eb24776ae19047c']
        target_path_scenes_just = 'http://{}:{}/api/{}'.format(
            self.host, self.port, 'scenes')
        target_path_scene_just_2 = 'http://{}:{}/api/{}'.format(
            self.host, self.port,
            'scenes/77d8548a5def0e7a410259296eb24776ae19047c')

        with responses.RequestsMock() as rsps:
            rsps.add(
                responses.GET, target_path_scenes_just,
                json=json.dumps(self.active_scenes), status=200)
            rsps.add(
                responses.GET, target_path_scene_just_2,
                json=json.dumps(self.loaded_datasets), status=200)

            res = do_scenes.scenes_list(self.c_data, just=just)
            self.assertEqual(res, just)

        # The scene we JUST want to display does not exist
        just = ['no_such_scene']
        target_path_scenes_just = 'http://{}:{}/api/{}'.format(
            self.host, self.port, 'scenes')

        with responses.RequestsMock() as rsps:
            rsps.add(
                responses.GET, target_path_scenes_just,
                json=json.dumps(self.active_scenes), status=200)

            res = do_scenes.scenes_list(self.c_data, just=just)
            self.assertEqual(res, [])

        # just is not a list but something else
        with self.assertRaises(TypeError):
            do_scenes.scenes_list(self.c_data, just='not_a_list')

    # @responses.activate
    def test_scenes_create(self):
        """Create a new scene

        """
        pass

if __name__ == '__main__':
    unittest.main(verbosity=2)
