#!/usr/bin/env python3
"""
Tests for parser.py

"""
import unittest
import unittest.mock as mock

import struct
import numpy as np
import pathlib
import re

import os
import sys
sys.path.append(os.path.join('..'))
import dataset_parser as dp
import binary_formats


class Test_parser(unittest.TestCase):

    def setUp(self):
        """
        We use actual data for testing. I don't want to mock this crap... Maybe
        later.

        """

        self.alt_ds = pathlib.Path('../object_a_small')
        self.ts = '00.1'
        self.field = 'nt11'

        self.path_dataset = pathlib.Path('../numsim.napf.tiefziehversuch')

        self.ts_1 = '0.007500045001506805419921875'
        self.ts_2 = '0.012500010430812835693359375'
        self.ts_3 = '0.0175000019371509552001953125'

        self.nodes = 'nodes.bin'
        self.elements_c3d6 = 'elements.c3d6.bin'
        self.elements_c3d8 = 'elements.c3d8.bin'

        self.LE0 = 'LE0.bin'
        self.LE0_name = 'LE0'

        self.mock_nodes = (.0, .1, .2, .3, .4, .5, .6, .7, .8)  # 3 points, 1 unit
        self.mock_nodes_bin_data = struct.pack('<{}d'.format(len(self.mock_nodes)), *self.mock_nodes)
        self.mock_nodes_hash = '445168d5b52ccc9cde21535e9fe7db6b8f5257dc'

        self.mock_c3d6 = (1, 1, 1, 2, 2, 3, 1, 1, 1, 2, 2, 3, 1, 1, 1, 2, 2, 3)  # 3 units
        self.mock_c3d6_bin_data = struct.pack('<{}i'.format(len(self.mock_c3d6)), *self.mock_c3d6)
        self.mock_c3d6_hash = '6c7542527749f04941397fda77e5ae7d6ee311c0'

        self.mock_c3d8 = (1, 2, 3, 4, 5, 6, 1, 1, 1, 2, 2, 3, 1, 1, 1, 2, 2, 3, 1, 1, 1, 2, 2, 3)  # 3 units
        self.mock_c3d8_bin_data = struct.pack('<{}i'.format(len(self.mock_c3d8)), *self.mock_c3d8)
        self.mock_c3d8_hash = 'b5ff493b4668063fdcdf451b96d42624820fa333'

        self.hash_of_c3d6_c3d8_nodes = '91f126d72b122ce78982d3d0b45524bd830c69f9'

        self.mock_field = (.1, .2, .3, .4, .5, .6)
        self.mock_field_bin_data = struct.pack('<{}d'.format(len(self.mock_field)), *self.mock_field)
        self.mock_field_hash = '995dfe801103a5b122fa30e937925e8cf0845d8b'

    def test_class(self):
        """Initialize the class

        """
        mp = dp.ParseDataset(self.path_dataset)
        self.assertIsInstance(mp, dp.ParseDataset)

        with self.assertRaises(TypeError):
            dp.ParseDataset('not_os_pathlike')

    def test__file_hash(self):
        """Generate a hash for a file we read in

        """
        valid_binary_path = self.path_dataset / 'fo' / self.ts_1 / self.nodes

        mp = dp.ParseDataset(self.path_dataset)

        with mock.patch('builtins.open', mock.mock_open(read_data=self.mock_nodes_bin_data)) as mock_bin:
            file_hash = mp._file_hash(valid_binary_path)
            mock_bin.assert_called_with(valid_binary_path, 'rb')

            self.assertRegex(file_hash, '^[0-9a-f]{40}$')

        # file does not exist, method should return None
        invalid_binary_path = self.path_dataset / 'fo' / self.ts_1 / self.nodes / 'nonexisting'

        res = mp._file_hash(invalid_binary_path)
        self.assertIsNone(res)

    def test__read_binary_data(self):
        """Read data from a binary file

        """
        valid_binary_path = self.path_dataset / 'fo' / self.ts_1 / self.nodes
        valid_fmt = binary_formats.nodes()

        expected_res = np.asarray(self.mock_nodes)
        expected_res.shape = (3, 3)

        mp = dp.ParseDataset(self.path_dataset)

        # result is as expected
        with mock.patch('builtins.open', mock.mock_open(read_data=self.mock_nodes_bin_data)) as mock_bin:
            res = mp._read_binary_data(valid_binary_path, valid_fmt)

            mock_bin.assert_called_with(valid_binary_path, 'rb')

            self.assertIsInstance(res, type(np.asarray([])))
            np.testing.assert_equal(res, expected_res)

        invalid_fmt = {
            '1': 8,
            '2': 'd',
            '3': 3
        }

        with self.assertRaises(KeyError):
            mp._read_binary_data(valid_binary_path, invalid_fmt)

    def xtest__model_free_faces(self):
        """Generate the surface of the model

        """
        mp = dp.ParseDataset(self.path_dataset)
        valid_binary_path = self.path_dataset / 'fo' / self.ts_1

        mesh_data = mp._mesh_data(valid_binary_path)
        nodes_data = mesh_data['nodes']
        elements_data = mesh_data['elements']

        res = mp._model_free_faces(nodes_data, elements_data)
        # print(res)


    def test__mesh_data(self):
        """Return the nodes and elements of the mesh

        """
        mp = dp.ParseDataset(self.path_dataset)
        valid_binary_path = self.path_dataset / 'fo' / self.ts_1 / self.nodes

        # fml...
        # all in order, no hash set, so we return the full data
        with mock.patch('dataset_parser.ParseDataset._file_hash', return_value=self.mock_nodes_hash) as mock_nodes_hash:
            with mock.patch('builtins.sorted', return_value=[1]) as mock_sort_nodes:
                with mock.patch('builtins.sorted', return_value=[1, 2]) as mock_sort_elements:
                    with mock.patch('re.search', side_effect=[
                            re.search('(c3d6)', 'c3d6'),
                            re.search('(c3d8)', 'c3d8')
                    ]) as mock_search:
                        with mock.patch('dataset_parser.ParseDataset._file_hash', return_value=self.mock_c3d6_hash) as mock_c3d6_hash:
                            with mock.patch('dataset_parser.ParseDataset._file_hash', return_value=self.mock_c3d8_hash) as mock_c3d8_hash:
                                with mock.patch('builtins.open', mock.mock_open(read_data=self.mock_nodes_bin_data)) as mock_nodes:
                                    with mock.patch('builtins.open', mock.mock_open(read_data=self.mock_c3d6_bin_data)) as mock_c3d6:
                                        with mock.patch('builtins.open', mock.mock_open(read_data=self.mock_c3d8_bin_data)) as mock_c3d8:
                                            res = mp._mesh_data(valid_binary_path)

                                            self.assertIsInstance(res, dict)
                                            self.assertIn('hash', res)
                                            self.assertIn('nodes', res)
                                            self.assertIn('elements', res)
                                            self.assertIsInstance(res['elements'], dict)
                                            self.assertIn('c3d6', res['elements'])
                                            self.assertIn('c3d8', res['elements'])
                                            self.assertIsInstance(res['elements']['c3d6'], dict)
                                            self.assertIsInstance(res['elements']['c3d8'], dict)

                                            self.assertEqual(res['hash'], self.hash_of_c3d6_c3d8_nodes)

        # wrong hash set
        with mock.patch('dataset_parser.ParseDataset._file_hash', return_value=self.mock_nodes_hash) as mock_nodes_hash:
            with mock.patch('builtins.sorted', return_value=[1]) as mock_sort_nodes:
                with mock.patch('builtins.sorted', return_value=[1, 2]) as mock_sort_elements:
                    with mock.patch('re.search', side_effect=[
                            re.search('(c3d6)', 'c3d6'),
                            re.search('(c3d8)', 'c3d8')
                    ]) as mock_search:
                        with mock.patch('dataset_parser.ParseDataset._file_hash', return_value=self.mock_c3d6_hash) as mock_c3d6_hash:
                            with mock.patch('dataset_parser.ParseDataset._file_hash', return_value=self.mock_c3d8_hash) as mock_c3d8_hash:
                                with mock.patch('builtins.open', mock.mock_open(read_data=self.mock_nodes_bin_data)) as mock_nodes:
                                    with mock.patch('builtins.open', mock.mock_open(read_data=self.mock_c3d6_bin_data)) as mock_c3d6:
                                        with mock.patch('builtins.open', mock.mock_open(read_data=self.mock_c3d8_bin_data)) as mock_c3d8:
                                            res = mp._mesh_data(valid_binary_path, 'some_wrong_hash')

                                            self.assertIsInstance(res, dict)
                                            self.assertIn('hash', res)
                                            self.assertIn('nodes', res)
                                            self.assertIn('elements', res)
                                            self.assertIsInstance(res['elements'], dict)
                                            self.assertIn('c3d6', res['elements'])
                                            self.assertIn('c3d8', res['elements'])
                                            self.assertIsInstance(res['elements']['c3d6'], dict)
                                            self.assertIsInstance(res['elements']['c3d8'], dict)

                                            self.assertEqual(res['hash'], self.hash_of_c3d6_c3d8_nodes)

        # all in order, hash set, so we return None
        with mock.patch('dataset_parser.ParseDataset._file_hash', return_value=self.mock_nodes_hash) as mock_nodes_hash:
            with mock.patch('builtins.sorted', return_value=[1]) as mock_sort_nodes:
                with mock.patch('builtins.sorted', return_value=[1, 2]) as mock_sort_elements:
                    with mock.patch('re.search', side_effect=[
                            re.search('(c3d6)', 'c3d6'),
                            re.search('(c3d8)', 'c3d8')
                    ]) as mock_search:
                        with mock.patch('dataset_parser.ParseDataset._file_hash', return_value=self.mock_c3d6_hash) as mock_c3d6_hash:
                            with mock.patch('dataset_parser.ParseDataset._file_hash', return_value=self.mock_c3d8_hash) as mock_c3d8_hash:
                                with mock.patch('builtins.open', mock.mock_open(read_data=self.mock_nodes_bin_data)) as mock_nodes:
                                    with mock.patch('builtins.open', mock.mock_open(read_data=self.mock_c3d6_bin_data)) as mock_c3d6:
                                        with mock.patch('builtins.open', mock.mock_open(read_data=self.mock_c3d8_bin_data)) as mock_c3d8:
                                            res = mp._mesh_data(valid_binary_path, current_hash=self.hash_of_c3d6_c3d8_nodes)

                                            self.assertIsInstance(res, dict)
                                            self.assertIn('hash', res)
                                            self.assertIn('nodes', res)
                                            self.assertIn('elements', res)

                                            self.assertEqual(res['hash'], self.hash_of_c3d6_c3d8_nodes)

                                            self.assertIsNone(res['nodes'])
                                            self.assertIsNone(res['elements'])

    def test__field_data(self):
        """Return field data

        """
        mp = dp.ParseDataset(self.path_dataset)
        valid_binary_path = self.path_dataset / 'fo' / self.ts_1 / self.nodes
        field_paths = [pathlib.Path('nodesssss.bin'), pathlib.Path('no/temps.bin')]

        # all in order
        with mock.patch('builtins.sorted', return_value=field_paths) as mock_sorted:
            with mock.patch('builtins.open', mock.mock_open(read_data=self.mock_field_bin_data)) as mock_field:
                with mock.patch('dataset_parser.ParseDataset._file_hash', return_value=self.mock_field_hash) as mock_field_hash:
                    res = mp._field_data(valid_binary_path, 'temps')

                    self.assertIsInstance(res, dict)
                    self.assertIn('hash', res)
                    self.assertEqual(res['hash'], self.mock_field_hash)
                    self.assertIn('field', res)
                    self.assertIsNotNone(res['field'])

        # all in order, current hash set
        with mock.patch('builtins.sorted', return_value=field_paths) as mock_sorted:
            with mock.patch('builtins.open', mock.mock_open(read_data=self.mock_field_bin_data)) as mock_field:
                with mock.patch('dataset_parser.ParseDataset._file_hash', return_value=self.mock_field_hash) as mock_field_hash:
                    res = mp._field_data(valid_binary_path, 'temps', current_hash=self.mock_field_hash)

                    self.assertIsInstance(res, dict)
                    self.assertIn('hash', res)
                    self.assertEqual(res['hash'], self.mock_field_hash)
                    self.assertIn('field', res)
                    self.assertIsNone(res['field'])

        # all in order, current hash set but wrong
        with mock.patch('builtins.sorted', return_value=field_paths) as mock_sorted:
            with mock.patch('builtins.open', mock.mock_open(read_data=self.mock_field_bin_data)) as mock_field:
                with mock.patch('dataset_parser.ParseDataset._file_hash', return_value=self.mock_field_hash) as mock_field_hash:
                    res = mp._field_data(valid_binary_path, 'temps', current_hash='wrng')

                    self.assertIsInstance(res, dict)
                    self.assertIn('hash', res)
                    self.assertEqual(res['hash'], self.mock_field_hash)
                    self.assertIn('field', res)
                    self.assertIsNotNone(res['field'])

    def test_timestep_field(self):
        """Read the field values for a given timestep

        """
        # altmp = dp.ParseDataset(self.alt_ds)
        # timestep_data = altmp.timestep_data(self.ts, self.field)
        mp = dp.ParseDataset(self.path_dataset)
        timestep_data = mp.timestep_data(self.ts_1, self.LE0_name)

        self.assertIsInstance(timestep_data, dict)
        self.assertIn('nodes', timestep_data)
        self.assertIn('field', timestep_data)
        self.assertIn('wireframe', timestep_data)
        self.assertIn('free_edges', timestep_data)
        self.assertIsNotNone(timestep_data['nodes'])
        self.assertIsNotNone(timestep_data['wireframe'])
        self.assertIsNotNone(timestep_data['free_edges'])
        self.assertIsNotNone(timestep_data['field'])

        print(len(timestep_data['nodes']['data']))
        print(len(timestep_data['field']['data']))

        hash_dict = {
            'field': '0c7b8cd841d8cf2384a9f9045838c21b0fce3797',
            'mesh': '309bbde203ef93a0fbc28b5eb213cda4cd16c211'
        }
        timestep_data = mp.timestep_data(self.ts_1, self.LE0_name, hash_dict=hash_dict)

        self.assertIsInstance(timestep_data, dict)

        timestep_data = mp.timestep_data(self.ts_1, 'non_existing')

        self.assertIsInstance(timestep_data, dict)
        self.assertIsNone(timestep_data['nodes'])
        self.assertIsNone(timestep_data['wireframe'])
        self.assertIsNone(timestep_data['free_edges'])
        self.assertIsNotNone(timestep_data['field'])

        # type mismatch
        with self.assertRaises(TypeError):
            mp.timestep_data(True, self.LE0_name)

        with self.assertRaises(TypeError):
            mp.timestep_data(self.ts_1, True)

        with self.assertRaises(TypeError):
            mp.timestep_data(self.ts_1, self.LE0_name, hash_dict='not_dict')

if __name__ == '__main__':
    unittest.main(verbosity=2)
