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

    def test_add_datasets(self):
        """
        Test adding one or more objects.

        """
        # Should not contain addDatasetsFail
        dataset_list_success = ['just_fo', 'another_just_fo']
        success_dict = _ScenePrototype(self.data_dir_path).add_datasets(dataset_list_success)
        self.assertIsInstance(success_dict, dict)
        self.assertIn('href', success_dict)
        self.assertIn('addDatasetsSuccess', success_dict)
        self.assertNotIn('addDatasetsFail', success_dict)

        # Appending identical datasets, should not contain addDatasetsFail
        dataset_list_success = ['just_fo', 'another_just_fo', 'just_fo', 'another_just_fo']
        success_dict = _ScenePrototype(self.data_dir_path).add_datasets(dataset_list_success)
        self.assertIsInstance(success_dict, dict)
        self.assertIn('href', success_dict)
        self.assertIn('addDatasetsSuccess', success_dict)
        self.assertNotIn('addDatasetsFail', success_dict)

        # Should contain both addDatasetsSuccess and addDatasetsFail
        dataset_list_partial = ['no_such_thing', 'another_just_fo']
        partial_dict = _ScenePrototype(self.data_dir_path).add_datasets(dataset_list_partial)
        self.assertIsInstance(partial_dict, dict)
        self.assertIn('href', partial_dict)
        self.assertIn('addDatasetsSuccess', partial_dict)
        self.assertIn('addDatasetsFail', partial_dict)

        # Should contain both addDatasetsSuccess and addDatasetsFail
        dataset_list_partial_not_just_string = ['no_such_thing', 'another_just_fo', 123]
        partial_dict_not_just_string = _ScenePrototype(self.data_dir_path).add_datasets(dataset_list_partial_not_just_string)
        self.assertIsInstance(partial_dict_not_just_string, dict)
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
        """
        Test listing the datasets.

        """
        # Construct the scene
        dataset_list_one = ['just_fo']
        dataset_list_two = ['just_fo', 'another_just_fo']

        # Append one element to it
        scene = _ScenePrototype(self.data_dir_path)
        scene.add_datasets(dataset_list_one)
        datasets = scene.list_datasets()
        self.assertTrue(len(datasets) == 1)

        # Append two more elements, now there are three in it
        scene.add_datasets(dataset_list_two)
        datasets = scene.list_datasets()
        self.assertTrue(len(datasets) == 3)

        # Each is a sha1 sum
        for entry in datasets:
            self.assertRegex(entry, '^[0-9a-f]{40}$')

    def test_delete_dataset(self):
        """
        Test removing one dataset.

        """
        # First construct the scene
        dataset_list = ['just_fo', 'just_fo', 'another_just_fo']
        scene = _ScenePrototype(self.data_dir_path)
        scene.add_datasets(dataset_list)
        cmp_datasets = scene.list_datasets()

        # Remove the 0th element
        dataset_to_delete = cmp_datasets[0]
        cmp_datasets.remove(dataset_to_delete)

        # Delete this element from the scene
        scene.delete_dataset(dataset_to_delete)
        res_dataset = scene.list_datasets()

        self.assertTrue(cmp_datasets == res_dataset)

        # List raises TypeError
        dataset_list = ['just_fo', 'just_fo', 'another_just_fo']
        scene = _ScenePrototype(self.data_dir_path)
        scene.add_datasets(dataset_list)
        cmp_datasets = scene.list_datasets()

        dataset_to_delete_list = [cmp_datasets[0]]

        with self.assertRaises(TypeError):
            scene.delete_dataset(dataset_to_delete_list)

    # IT IS NOT NECESSARY TO TEST FOR THIS BECAUSE THE API DOES NOT SPECIFY THIS.
    # def test_delete_datasetss(self):
    #     """
    #     Test deleting datasets from the scene.

    #     """
    #     # First construct the scene
    #     dataset_list = ['just_fo', 'just_fo', 'another_just_fo']
    #     scene_one = _ScenePrototype(self.data_dir_path)
    #     scene_one.add_datasets(dataset_list)
    #     cmp_datasets_one = scene_one.list_datasets()

    #     self.assertTrue(len(cmp_datasets_one) == 3)

    #     dataset_to_delete = cmp_datasets_one[0]
    #     delete_list = [dataset_to_delete]
    #     scene_one.delete_datasets(delete_list)
    #     res_datasets_one = scene_one.list_datasets()

    #     self.assertFalse(len(res_datasets_one) == 3)
    #     self.assertTrue(len(res_datasets_one) == 2)

    #     # Removing two has one left
    #     dataset_list = ['just_fo', 'just_fo', 'another_just_fo']
    #     scene_two = _ScenePrototype(self.data_dir_path)
    #     scene_two.add_datasets(dataset_list)
    #     cmp_datasets_two = scene_two.list_datasets()
    #     self.assertTrue(len(cmp_datasets_two) == 3)
    #     datasets_to_delete_list = cmp_datasets_two[0:2]  # Get the first two

    #     scene_two.delete_datasets(datasets_to_delete_list)
    #     res_datasets_two = scene_two.list_datasets()

    #     self.assertFalse(len(res_datasets_two) == 3)
    #     self.assertTrue(len(res_datasets_two) == 1)

    #     # Removing all the datasets should yield an exception to be caught
    #     dataset_list = ['just_fo', 'just_fo', 'another_just_fo']
    #     scene_three = _ScenePrototype(self.data_dir_path)
    #     scene_three.add_datasets(dataset_list)
    #     cmp_datasets_three = scene_three.list_datasets()

    #     with self.assertRaises(IndexError):
    #         scene_three.delete_datasets(cmp_datasets_three)


    #     # String or smth raises TypeError
    #     scene_four = _ScenePrototype(self.data_dir_path)
    #     scene_four.add_datasets(dataset_list)
    #     cmp_datasets_four = scene_four.list_datasets()
    #     dataset_to_delete = cmp_datasets_four[0]

    #     with self.assertRaises(TypeError):
    #         scene_four.delete_datasets(dataset_to_delete)


if __name__ == '__main__':
    """
    Testing as standalone program.

    """
    unittest.main(verbosity=2)
