#!/usr/bin/env python3
"""
Tests for backend.scenes_scene_prototype

"""
import unittest
import pathlib

# Append the parent directory for importing the file.
import sys
import os
sys.path.append(os.path.join('..', '..'))  # Append the program root dir
from backend.scenes_scene_prototype import _ScenePrototype


class Test_scenes_scene_prototype(unittest.TestCase):

    def setUp(self):
        """
        Setup the test case.

        """
        file_path = os.path.dirname(__file__)
        self.data_dir_string = 'mock_data'
        self.data_dir_path = pathlib.Path('{}/{}'.format(
            file_path, self.data_dir_string))

    def test_init(self):
        """
        Test the scene init.

        """
        self.assertIsInstance(_ScenePrototype(self.data_dir_path), _ScenePrototype)

        data_dir_string = 'mock_data'
        with self.assertRaises(TypeError):
            _ScenePrototype(data_dir_string)

        non_existing_dataset = self.data_dir_path / 'does_not_exist'
        with self.assertRaises(ValueError):
            _ScenePrototype(non_existing_dataset)

    def test_scene_name_is_sha1(self):
        """
        Test if the format is correct, that is 40 hex chars.

        Regex this: '^[0-9a-f]{40}$'

        ^        Start Of String Anchor
        [0-9a-f] Any of the following characters: 0123456789abcdef
        {40}     Repeated 40 times
        $        End Of String Anchor

        Adapted from https://stackoverflow.com/questions/2982059/testing-if-string-is-sha1-in-php

        """
        scene_name = _ScenePrototype(self.data_dir_path).name()
        self.assertRegex(scene_name, '^[0-9a-f]{40}$')

    def test__add_one_dataset(self):
        """
        Test what happens when we want to add one dataset.

        """
        just_fo_string = 'just_fo'
        dataset_path = self.data_dir_path / just_fo_string

        # Correct path
        dataset_meta = _ScenePrototype(self.data_dir_path)._add_one_dataset(dataset_path)
        self.assertIsInstance(dataset_meta, dict)
        self.assertIn('datasetAlias', dataset_meta)
        self.assertIn('datasetHash', dataset_meta)
        self.assertIn('datasetHref', dataset_meta)
        self.assertIn('datasetName', dataset_meta)

        # Wrong argument type
        with self.assertRaises(TypeError):
            _ScenePrototype(self.data_dir_path)._add_one_dataset('{}/{}.'.format(
                self.data_dir_string, just_fo_string))

        # Non exising path
        non_existing_path = dataset_path / 'does_not_exist'
        with self.assertRaises(ValueError):
            _ScenePrototype(self.data_dir_path)._add_one_dataset(non_existing_path)

        # Points to file instead of dir
        not_a_dir = dataset_path / 'not_a_directory'
        with self.assertRaises(ValueError):
            _ScenePrototype(self.data_dir_path)._add_one_dataset(not_a_dir)

    def test_add_dataset(self):
        """
        Test adding one or more objects.
        """
        # Should not contain addDatasetsFail
        dataset_list_success = ['just_fo', 'another_just_fo']
        success_dict = _ScenePrototype(self.data_dir_path).add_dataset(dataset_list_success)
        self.assertIsInstance(success_dict, dict)
        self.assertIn('href', success_dict)
        self.assertIn('addDatasetsSuccess', success_dict)
        self.assertNotIn('addDatasetsFail', success_dict)

        # Should contain both addDatasetsSuccess and addDatasetsFail
        dataset_list_partial = ['no_such_thing', 'another_just_fo']
        partial_dict = _ScenePrototype(self.data_dir_path).add_dataset(dataset_list_partial)
        self.assertIsInstance(partial_dict, dict)
        self.assertIn('href', partial_dict)
        self.assertIn('addDatasetsSuccess', partial_dict)
        self.assertIn('addDatasetsFail', partial_dict)

        # Just return None
        dataset_list_fail = ['just_fo_', 'another_just_fo_']
        fail_return = _ScenePrototype(self.data_dir_path).add_dataset(dataset_list_fail)
        self.assertIsNone(fail_return)

        # Empty list should fail
        empty_list = []
        with self.assertRaises(ValueError):
            _ScenePrototype(self.data_dir_path).add_dataset(empty_list)

        just_a_string = 'just_fo'
        with self.assertRaises(TypeError):
            _ScenePrototype(self.data_dir_path).add_dataset(just_a_string)

if __name__ == '__main__':
    """
    Testing as standalone program.

    """
    unittest.main(verbosity=2)
