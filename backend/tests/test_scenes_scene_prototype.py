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
from backend.scenes_dataset_prototype import _DatasetPrototype


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
        """Init the scene_prototype."""
        self.assertIsInstance(_ScenePrototype(self.data_dir_path), _ScenePrototype)

        data_dir_string = 'mock_data'
        with self.assertRaises(TypeError):
            _ScenePrototype(data_dir_string)

        non_existing_dataset = self.data_dir_path / 'does_not_exist'
        with self.assertRaises(ValueError):
            _ScenePrototype(non_existing_dataset)

        # Test if the format is correct, that is 40 hex chars.
        #
        # Regex this: '^[0-9a-f]{40}$'
        #
        # ^        Start Of String Anchor
        # [0-9a-f] Any of the following characters: 0123456789abcdef
        # {40}     Repeated 40 times
        # $        End Of String Anchor
        #
        # Adapted from https://stackoverflow.com/questions/2982059/testing-if-string-is-sha1-in-php
        #
        scene_name = _ScenePrototype(self.data_dir_path).name()
        self.assertRegex(scene_name, '^[0-9a-f]{40}$')

    def test__add_dataset(self):
        """Add ONE dataset."""

        scene = _ScenePrototype(self.data_dir_path)

        datasets = scene.list_datasets()
        self.assertTrue(len(datasets) == 0)

        just_fo_string = 'just_fo'
        dataset_path = self.data_dir_path / just_fo_string

        # Returns dataset hash
        dataset_hash = scene._add_dataset(dataset_path)
        self.assertIsInstance(dataset_hash, str)
        self.assertRegex(dataset_hash, '^[0-9a-f]{40}$')

        datasets = scene.list_datasets()
        self.assertTrue(len(datasets) == 1)

        # Wrong argument type
        with self.assertRaises(TypeError):
            _ScenePrototype(self.data_dir_path)._add_dataset('{}/{}.'.format(
                self.data_dir_string, just_fo_string))

        # Non exising path
        non_existing_path = dataset_path / 'does_not_exist'
        with self.assertRaises(ValueError):
            _ScenePrototype(self.data_dir_path)._add_dataset(non_existing_path)

        # Points to file instead of dir
        not_a_dir = dataset_path / 'not_a_directory'
        with self.assertRaises(ValueError):
            _ScenePrototype(self.data_dir_path)._add_dataset(not_a_dir)

    def test_add_datasets(self):
        """Add one or more datasets in a list."""

        # Should not contain addDatasetsFail
        dataset_list_success = ['just_fo', 'another_just_fo']
        success_dict = _ScenePrototype(self.data_dir_path).add_datasets(dataset_list_success)
        self.assertIsInstance(success_dict, dict)
        self.assertIn('sceneHash', success_dict)
        self.assertIn('href', success_dict)
        self.assertIn('addDatasetsSuccess', success_dict)
        self.assertNotIn('addDatasetsFail', success_dict)

        # addDatasetsSuccess should contain meta_data of a dataset
        dataset_meta = success_dict['addDatasetsSuccess'][0]
        self.assertIsInstance(dataset_meta, dict)
        self.assertIn('sceneHash', success_dict)
        self.assertIn('datasetAlias', dataset_meta)
        self.assertIn('datasetHash', dataset_meta)
        self.assertIn('datasetHref', dataset_meta)
        self.assertIn('datasetName', dataset_meta)

        # Appending identical datasets, should not contain addDatasetsFail
        dataset_list_success = ['just_fo', 'another_just_fo', 'just_fo', 'another_just_fo']
        success_dict = _ScenePrototype(self.data_dir_path).add_datasets(dataset_list_success)
        self.assertIsInstance(success_dict, dict)
        self.assertIn('sceneHash', success_dict)
        self.assertIn('href', success_dict)
        self.assertIn('addDatasetsSuccess', success_dict)
        self.assertNotIn('addDatasetsFail', success_dict)

        # Should contain both addDatasetsSuccess and addDatasetsFail
        dataset_list_partial = ['no_such_thing', 'another_just_fo']
        partial_dict = _ScenePrototype(self.data_dir_path).add_datasets(dataset_list_partial)
        self.assertIsInstance(partial_dict, dict)
        self.assertIn('sceneHash', success_dict)
        self.assertIn('href', partial_dict)
        self.assertIn('addDatasetsSuccess', partial_dict)
        self.assertIn('addDatasetsFail', partial_dict)

        # Should contain both addDatasetsSuccess and addDatasetsFail
        dataset_list_partial_not_just_string = ['no_such_thing', 'another_just_fo', 123]
        partial_dict_not_just_string = _ScenePrototype(self.data_dir_path).add_datasets(dataset_list_partial_not_just_string)
        self.assertIsInstance(partial_dict_not_just_string, dict)
        self.assertIn('sceneHash', success_dict)
        self.assertIn('href', partial_dict_not_just_string)
        self.assertIn('addDatasetsSuccess', partial_dict_not_just_string)
        self.assertIn('addDatasetsFail', partial_dict_not_just_string)

        # Just return None
        dataset_list_fail = ['just_fo_', 'another_just_fo_']
        fail_return = _ScenePrototype(self.data_dir_path).add_datasets(dataset_list_fail)
        self.assertIsNone(fail_return)

        # Empty list should fail
        empty_list = []
        with self.assertRaises(ValueError):
            _ScenePrototype(self.data_dir_path).add_datasets(empty_list)

        just_a_string = 'just_fo'
        with self.assertRaises(TypeError):
            _ScenePrototype(self.data_dir_path).add_datasets(just_a_string)

    def test_list_datasets(self):
        """List datasets in a scene."""
        # Construct the scene
        scene = _ScenePrototype(self.data_dir_path)

        datasets = scene.list_datasets()

        self.assertIsInstance(datasets, list)
        self.assertTrue(len(datasets) == 0)

        # Append two valid datasets
        scene._add_dataset(self.data_dir_path / 'just_fo')
        scene._add_dataset(self.data_dir_path / 'another_just_fo')

        datasets = scene.list_datasets()
        for dataset in datasets:
            self.assertIsInstance(dataset, str)
            self.assertRegex(dataset, '^[0-9a-f]{40}$')
        self.assertTrue(len(datasets) == 2)

    def test_delete_dataset(self):
        """Remove ONE dataset from a scene."""
        # Construct the scene
        scene = _ScenePrototype(self.data_dir_path)

        # Append three valid datasets
        scene._add_dataset(self.data_dir_path / 'just_fo')
        scene._add_dataset(self.data_dir_path / 'just_fo')
        scene._add_dataset(self.data_dir_path / 'another_just_fo')

        cmp_datasets = scene.list_datasets()
        self.assertTrue(len(cmp_datasets) == 3)

        # Remove the 0th element from the compare list
        dataset_to_delete = cmp_datasets.pop(0)

        # Delete this element from the scene
        scene.delete_dataset(dataset_to_delete)

        # Do we have two elements left?
        cmp_datasets = scene.list_datasets()
        self.assertTrue(len(cmp_datasets) == 2)

        # Successful delete returns the remaining datasets in the scene
        dataset_to_delete = cmp_datasets.pop(0)
        remaining_datasets = scene.delete_dataset(dataset_to_delete)
        self.assertIsInstance(remaining_datasets, list)
        self.assertTrue(cmp_datasets == remaining_datasets)

        # We have to supply a string as a dataset_hash
        dataset_to_delete = [cmp_datasets[0]]
        with self.assertRaises(TypeError):
            scene.delete_dataset(dataset_to_delete)

        # If we supply the wrong hash we expect a ValueError
        dataset_to_delete = 'wrong'
        with self.assertRaises(ValueError):
            scene.delete_dataset(dataset_to_delete)

        # Do we have one element left?
        cmp_datasets = scene.list_datasets()
        self.assertFalse(len(cmp_datasets) == 0)
        self.assertFalse(len(cmp_datasets) == 2)
        self.assertTrue(len(cmp_datasets) == 1)

        # Delete the last dataset and let it return something
        dataset_to_delete = cmp_datasets.pop(0)
        remaining_datasets = scene.delete_dataset(dataset_to_delete)
        self.assertIsInstance(remaining_datasets, list)
        self.assertTrue(cmp_datasets == remaining_datasets)
        self.assertTrue(len(cmp_datasets) == 0)

    def test_dataset(self):
        """Return a dataset object."""
        # Construct the scene
        scene = _ScenePrototype(self.data_dir_path)

        # Append three valid datasets
        scene._add_dataset(self.data_dir_path / 'just_fo')
        scene._add_dataset(self.data_dir_path / 'another_just_fo')

        cmp_datasets = scene.list_datasets()
        self.assertTrue(len(cmp_datasets) == 2)

        # Try and access one dataset, it should return an object
        target_dataset_hash = cmp_datasets[0]
        target_dataset = scene.dataset(target_dataset_hash)
        self.assertIsInstance(target_dataset, _DatasetPrototype)

        # We have to supply a string as a dataset_hash
        dataset_wrong = [cmp_datasets[0]]
        with self.assertRaises(TypeError):
            scene.delete_dataset(dataset_wrong)

        # If we supply the wrong hash we expect a ValueError
        dataset_wrong = 'wrong'
        with self.assertRaises(ValueError):
            scene.dataset(dataset_wrong)

if __name__ == '__main__':
    """
    Testing as standalone program.

    """
    unittest.main(verbosity=2)
