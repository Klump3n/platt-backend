#!/usr/bin/env python3
"""
Tests for backend.scenes_dataset_prototype

"""
import numpy as np
import unittest
import pathlib

# Append the parent directory for importing the file.
import sys
import os
sys.path.append(os.path.join('..', '..'))  # Append the program root dir
from backend.scenes_dataset_prototype import _DatasetPrototype


class Test_scenes_dataset_prototype(unittest.TestCase):

    def setUp(self):
        """
        Set up the test case.

        """
        # Set the path to a mock dataset
        file_path = os.path.dirname(__file__)
        self.valid_dir_name = 'just_fo'
        self.string_path = '{}/mock_data/{}'.format(
            file_path, self.valid_dir_name)

        self.valid_path = pathlib.Path(self.string_path)
        self.invalid_path = pathlib.Path('dir_does_not_exist')
        self.test_dataset_object = _DatasetPrototype(self.valid_path)

    def test_valid_path_instatiates_dataset(self):
        """
        Check if the dataset instantiates.

        """
        valid_path_dataset = self.test_dataset_object
        self.assertIsInstance(valid_path_dataset, _DatasetPrototype)

    def test_invalid_path_raises_ValueError(self):
        """
        An invalid path raises a ValueError

        """
        with self.assertRaises(ValueError):
            _DatasetPrototype(self.invalid_path)

    def test_string_path_returns_TypeError(self):
        """
        A string for a path raises a TypeError.

        """
        with self.assertRaises(TypeError):
            _DatasetPrototype(self.string_path)

    def test_returned_meta(self):
        """
        Test if the returned metadata dict is correct.

        """
        dataset_meta = self.test_dataset_object.meta()
        self.assertIsInstance(dataset_meta, dict)
        self.assertIn('datasetAlias', dataset_meta)
        self.assertIn('datasetHash', dataset_meta)
        self.assertIn('datasetHref', dataset_meta)
        self.assertIn('datasetName', dataset_meta)

    def test_returned_name_is_correct(self):
        """
        Test if the name that we assign is correct.

        """
        valid_dataset_name = self.test_dataset_object.meta()['datasetName']
        self.assertEqual(valid_dataset_name, self.valid_dir_name)

    def test_get_orientation(self):
        """
        Test getting the orientation from the dataset.

        """
        np.testing.assert_array_equal(
            self.test_dataset_object.orientation(), np.eye(4))

    def test_set_orientation(self):
        """
        Test setting the orientation for the dataset.

        """
        # Create some mock array data
        array_data = [
            [1.,  2.,  3.,  4.],
            [0.,  1.1,  0.2,  0.1],
            [-0.,  -1.,  -2.,  -3.],
            [-1.1,  -.1,  0.,  1.]
        ]
        np_array_data_three_by_three = np.eye(3)
        np_array_data = np.asarray(array_data)

        with self.assertRaises(TypeError):
            self.test_dataset_object.orientation(array_data)

        with self.assertRaises(ValueError):
            self.test_dataset_object.orientation(np_array_data_three_by_three)

        self.test_dataset_object.orientation(np_array_data)
        np.testing.assert_array_equal(
            self.test_dataset_object.orientation(), np_array_data)


if __name__ == '__main__':
    """
    Testing as standalone program.

    """
    unittest.main(verbosity=2)
