#!/usr/bin/env python3
"""
Unittest for dataset_load_data

"""
import unittest
import unittest.mock as mock

import numpy as np
import pathlib
import struct

import os
import sys
# Append the parent directory for importing the file.
sys.path.append(os.path.join('..', '..'))  # Append the program root dir
import backend.dataset_load_data as dataset_load_data


class Test_dataset_load_data(unittest.TestCase):
    """
    Test this shit.

    """
    def setUp(self):
        """Setup of test.

        """
        pass

    def test__get_binary_data(self):
        """Load binary data from file

        """
        data_path = pathlib.Path('.')

        data = dataset_load_data.LoadData(data_path)

        binary_file = pathlib.Path('.')
        binary_format = {
            'data_point_size': 8,
            'data_point_type': 'd',
            'points_per_unit': 3
        }

        mock_data = (.0, .1, .2, .3, .4, .5, .6, .7, .8)  # 3 points, 1 unit
        expected_res = np.array([[.0, .1, .2], [.3, .4, .5], [.6, .7, .8]])

        mock_bin_data = struct.pack('<{}d'.format(len(mock_data)), *mock_data)

        with mock.patch('builtins.open', mock.mock_open(read_data=mock_bin_data)) as mock_bin:
            res = data._get_binary_data(binary_file, binary_format)

            mock_bin.assert_called_with(binary_file, 'rb')

            self.assertIsInstance(res, type(np.asarray([])))
            np.testing.assert_equal(res, expected_res)

        # bin_file does not exist, returns None
        binary_file = pathlib.Path('non_existing')
        res = data._get_binary_data(binary_file, binary_format)
        self.assertIsNone(res)

        # malformed dict
        binary_file = pathlib.Path('.')
        binary_format = {
            'data_point': 8,
            'data_point': 'd',
            'points_per': 3
        }
        with self.assertRaises(KeyError):
            data._get_binary_data(binary_file, binary_format)

        # type mismatch
        with self.assertRaises(TypeError):
            data._get_binary_data('not_os.PathLike', binary_format)

        with self.assertRaises(TypeError):
            data._get_binary_data(binary_file, 'not_a_dict')


if __name__ == '__main__':
    unittest.main(verbosity=2)
