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
        """Set up the test case.

        """
        # Set the path to a mock dataset
        file_path = os.path.dirname(__file__)
        self.valid_dir_name = 'just_fo'  # this contains data too
        self.string_path = '{}/mock_data/{}'.format(
            file_path, self.valid_dir_name)

        self.valid_path = pathlib.Path(self.string_path)
        self.invalid_path = pathlib.Path('dir_does_not_exist')
        self.test_dataset_object = _DatasetPrototype(self.valid_path)

    def test_valid_path_instatiates_dataset(self):
        """Check if the dataset instantiates.

        """
        valid_path_dataset = self.test_dataset_object
        self.assertIsInstance(valid_path_dataset, _DatasetPrototype)

    def test_invalid_path_raises_ValueError(self):
        """An invalid path raises a ValueError

        """
        with self.assertRaises(ValueError):
            _DatasetPrototype(self.invalid_path)

    def test_string_path_returns_TypeError(self):
        """A string for a path raises a TypeError.

        """
        with self.assertRaises(TypeError):
            _DatasetPrototype(self.string_path)

    def test_returned_meta(self):
        """Test if the returned metadata dict is correct.

        """
        dataset_meta = self.test_dataset_object.meta()
        self.assertIsInstance(dataset_meta, dict)
        self.assertIn('datasetAlias', dataset_meta)
        self.assertIn('datasetHash', dataset_meta)
        self.assertIn('datasetHref', dataset_meta)
        self.assertIn('datasetName', dataset_meta)

    def test_returned_name_is_correct(self):
        """Test if the name that we assign is correct.

        """
        valid_dataset_name = self.test_dataset_object.meta()['datasetName']
        self.assertEqual(valid_dataset_name, self.valid_dir_name)

    def test_orientation(self):
        """GET and PATCH the orientation of a datasetName

        """
        unit_orient = [
            1, 0, 0, 0,
            0, 1, 0, 0,
            0, 0, 1, 0,
            0, 0, 0, 1
        ]

        # At first it's a 'unitary' list
        unitary = self.test_dataset_object.orientation()
        self.assertEqual(unitary, unit_orient)

        # Set it to something else
        new_orient = [
            1, 0, 0, 1,
            0, 1, 0, 0,
            0, 0, 1, 0,
            1, 0, 0, 5
        ]

        self.assertNotEqual(unit_orient, new_orient)
        new_return = self.test_dataset_object.orientation(new_orient)
        self.assertNotEqual(new_return, unit_orient)
        self.assertEqual(new_return, new_orient)

        # Type mismatch
        some_dict = {'well': 1}
        with self.assertRaises(TypeError):
            self.test_dataset_object.orientation(some_dict)

        # Length mismatch
        too_long = [
            1, 0, 0, 1,
            0, 1, 0, 0,
            0, 0, 1, 0,
            1, 0, 0, 1,
            0, 1, 0, 0,
            0, 0, 1, 0,
            1, 0, 0, 5
        ]

        with self.assertRaises(ValueError):
            self.test_dataset_object.orientation(too_long)

    def test_timestep_list(self):
        """Get a list of timesteps for the datasetName

        """
        expected_list = ['00.1', '00.2', '00.3', '00.4', '10.0', '10.4', '100.0', '100.4']
        res = self.test_dataset_object.timestep_list()

        self.assertEqual(expected_list, res)

    def test_timestep(self):
        """GET or PATCH the current timestep

        """
        # on init it is set to the lowest timestep
        expected_init_t = self.test_dataset_object.timestep_list()[0]
        res = self.test_dataset_object.timestep()
        self.assertEqual(expected_init_t, res)

        # set to some timestep in the list
        set_to = '00.4'
        res = self.test_dataset_object.timestep(set_to)
        self.assertEqual(res, set_to)

        # set to impossible timestep, should not change the timestep
        res = self.test_dataset_object.timestep('0')
        self.assertEqual(res, set_to)

        # type mismatch raises TypeError
        set_to = 1
        with self.assertRaises(TypeError):
            self.test_dataset_object.timestep(set_to)

    def test_field_dict(self):
        """Get a dcit of fields (elemental and nodal) for a given timestep

        """
        dataset = _DatasetPrototype(self.valid_path)

        # set the timestep
        timestep = '00.1'
        dataset.timestep(timestep)

        res = dataset.field_dict()

        self.assertIsInstance(res, dict)
        self.assertIn('elemental', res)
        self.assertIsInstance(res['elemental'], list)
        self.assertIn('nodal', res)
        self.assertIsInstance(res['nodal'], list)

        # 00.1 contains eo/an_element_field.bin and no/nt11.bin and no/some_mock_field.bin
        # .bin gets stripped
        self.assertEqual(sorted(res['elemental']), sorted(['an_element_field']))
        self.assertEqual(sorted(res['nodal']), sorted(['nt11', 'some_mock_field']))

    def test_field(self):
        """GET or PATCH (set) a field for a given dataset and timestep

        """
        dataset = _DatasetPrototype(self.valid_path)

        # set the timestep
        timestep = '00.1'
        dataset.timestep(timestep)

        # as no field is set it returns 'no_field'
        res = dataset.field()

        self.assertEqual(res, 'no_field')

        # this field exists
        new_field = 'nt11'
        res = dataset.field(set_field=new_field)

        self.assertEqual(res, new_field)

        # this field does not exist
        new_field = 'nt'
        res = dataset.field(set_field=new_field)

        self.assertEqual(res, 'no_field')

        # type mismatch
        with self.assertRaises(TypeError):
            dataset.field(set_field=1)

        # changing to another timestep that also has that field available preserves the selection
        timestep = '00.1'
        new_field = 'nt11'
        dataset.timestep(timestep)
        res = dataset.field(set_field=new_field)

        self.assertEqual(res, new_field)

        timestep = '00.2'
        dataset.timestep(timestep)
        res = dataset.field()

        self.assertEqual(res, new_field)

        timestep = '00.3'
        dataset.timestep(timestep)
        res = dataset.field()

        self.assertEqual(res, new_field)

        # changing to a timestep where a field does not exist does not reset the selection of a field
        # 00.1 has some_mock_field, 00.2 does not, 00.3 does again have that field
        timestep = '00.1'
        new_field = 'some_mock_field'
        dataset.timestep(timestep)
        res = dataset.field(set_field=new_field)

        self.assertEqual(res, new_field)

        timestep = '00.2'
        expected_res = 'no_field'
        dataset.timestep(timestep)
        res = dataset.field()

        self.assertEqual(res, expected_res)

        # the selected field is still stored in the dataset
        timestep = '00.3'
        dataset.timestep(timestep)
        res = dataset.field()

        self.assertEqual(res, new_field)


if __name__ == '__main__':
    """
    Testing as standalone program.

    """
    unittest.main(verbosity=2)
