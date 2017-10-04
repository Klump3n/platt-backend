#!/usr/bin/env python3
"""
Testing the scenes_manager

"""
import os
import sys
import unittest
import pathlib

# Append the parent directory for importing the file.
sys.path.append(os.path.join('..', '..'))  # Append the program root dir
from backend.scenes_manager import SceneManager
from backend.scenes_scene_prototype import _ScenePrototype
# from backend.scenes_dataset_prototype import _DatasetPrototype


class Test_SceneManager(unittest.TestCase):
    """
    Unittest for SimulationObject.
    """
    def setUp(self):
        """Setup the test case

        """
        file_path = os.path.dirname(__file__)
        self.data_dir_string = 'mock_data'
        self.data_dir_path = pathlib.Path('{}/{}'.format(
            file_path, self.data_dir_string))

    def test_SceneManager_init(self):
        """Init of SceneManager"""

        scene_manager = SceneManager(self.data_dir_path)
        self.assertIsInstance(scene_manager, SceneManager)
        with self.assertRaises(TypeError):
            scene_manager = SceneManager('a_string')

    def test_list_available_datasets(self):
        """Get a listing of the available datasets

        """
        expected_list = sorted(['just_fo', 'fo_and_frb', 'another_just_fo'])
        scene_manager = SceneManager(self.data_dir_path)
        returned_dict = scene_manager.list_available_datasets()
        self.assertIsInstance(returned_dict, dict)
        self.assertIn('availableDatasets', returned_dict)
        self.assertEqual(expected_list, returned_dict['availableDatasets'])

    def test_new_scene(self):
        """Create a new scene with some data

        """
        # This data exists
        dataset_list = ['just_fo', 'another_just_fo']

        scene_manager = SceneManager(self.data_dir_path)
        new_scene = scene_manager.new_scene(dataset_list)

        self.assertIsInstance(new_scene, dict)
        self.assertIn('sceneHash', new_scene)
        self.assertIn('href', new_scene)
        self.assertIn('addDatasetsSuccess', new_scene)
        self.assertNotIn('addDatasetsFail', new_scene)

        # This data partially exists
        dataset_list = ['just_fo__', 'another_just_fo']

        scene_manager = SceneManager(self.data_dir_path)
        new_scene = scene_manager.new_scene(dataset_list)

        self.assertIsInstance(new_scene, dict)
        self.assertIn('sceneHash', new_scene)
        self.assertIn('href', new_scene)
        self.assertIn('addDatasetsSuccess', new_scene)
        self.assertIn('addDatasetsFail', new_scene)

        # This data does not exist
        dataset_list = ['just_fo__', 'another_just_fo___']

        scene_manager = SceneManager(self.data_dir_path)
        new_scene = scene_manager.new_scene(dataset_list)

        self.assertIsNone(new_scene)

        # Create an empty scene should return None
        scene_manager = SceneManager(self.data_dir_path)
        new_scene = scene_manager.new_scene([])

        self.assertIsNone(new_scene)

        # Creating a scene with an invalid dataset should not create an empty
        # scene
        dataset_list = ['just_fo__']
        scene_manager = SceneManager(self.data_dir_path)

        listing = scene_manager.list_scenes()
        self.assertEqual(len(listing['activeScenes']), 0)

        new_scene = scene_manager.new_scene(dataset_list)
        listing = scene_manager.list_scenes()

        self.assertEqual(len(listing['activeScenes']), 0)


    def test_list_scenes(self):
        """List the active scenes on the server

        """
        dataset_list = ['just_fo', 'another_just_fo']
        scene_manager = SceneManager(self.data_dir_path)

        listing = scene_manager.list_scenes()

        self.assertIsInstance(listing, dict)
        self.assertIn('activeScenes', listing)
        self.assertEqual(len(listing['activeScenes']), 0)

        new_scene = scene_manager.new_scene(dataset_list)
        listing = scene_manager.list_scenes()

        self.assertEqual(len(listing['activeScenes']), 1)

        new_scene = scene_manager.new_scene(dataset_list)
        listing = scene_manager.list_scenes()

        self.assertEqual(len(listing['activeScenes']), 2)

        # That's just SHA1 strings
        for dataset in listing['activeScenes']:
            self.assertIsInstance(dataset, str)
            self.assertRegex(dataset, '^[0-9a-f]{40}$')

    def test_delete_scene(self):
        """Delete a scene

        """
        dataset_list = ['just_fo', 'another_just_fo']
        scene_manager = SceneManager(self.data_dir_path)

        listing = scene_manager.list_scenes()
        self.assertEqual(len(listing['activeScenes']), 0)

        scene_manager.new_scene(dataset_list)
        listing = scene_manager.list_scenes()

        self.assertEqual(len(listing['activeScenes']), 1)

        scene_hash = listing['activeScenes'][0]
        expected_dict = {
            'sceneDeleted': scene_hash,
            'href': '/scenes'
        }

        deleted_dict = scene_manager.delete_scene(scene_hash)

        self.assertIsInstance(deleted_dict, dict)
        self.assertEqual(expected_dict, deleted_dict)

        listing = scene_manager.list_scenes()

        self.assertEqual(len(listing['activeScenes']), 0)

        scene_manager.new_scene(dataset_list)
        listing = scene_manager.list_scenes()

        # wrong data type
        self.assertEqual(len(listing['activeScenes']), 1)
        with self.assertRaises(TypeError):
            scene_manager.delete_scene(1)

        # scene does not exist
        deleted_hash = scene_manager.delete_scene('some_string')
        self.assertIsInstance(deleted_hash, type(None))

    def test_scene(self):
        """Access a scene that was created

        """
        dataset_list = ['just_fo', 'another_just_fo']
        scene_manager = SceneManager(self.data_dir_path)
        new_scene = scene_manager.new_scene(dataset_list)

        # Access an existing scene
        new_scene_hash = new_scene['sceneHash']
        new_scene_object = scene_manager.scene(new_scene_hash)

        self.assertIsInstance(new_scene_object, _ScenePrototype)

        # Access a nonexisting scene
        new_scene_object = scene_manager.scene('something_else')

        self.assertIsNone(new_scene_object)

        # Something other than string raises a TypeError
        with self.assertRaises(TypeError):
            new_scene_object = scene_manager.scene(1)

    def test_add_datasets(self):
        """Add one or more datasets in a list

        """
        # Should not contain addDatasetsFail
        dataset_list = ['just_fo']
        scene_manager = SceneManager(self.data_dir_path)
        new_scene = scene_manager.new_scene(dataset_list)
        new_scene_hash = new_scene['sceneHash']

        loaded_dataset_dict = scene_manager.list_loaded_datasets(new_scene_hash)

        self.assertEqual(len(loaded_dataset_dict['loadedDatasets']), 1)

        add_datasets_list = ['just_fo', 'another_just_fo']

        success_dict = scene_manager.add_datasets(new_scene_hash, add_datasets_list)
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
        dataset_list = ['just_fo']
        scene_manager = SceneManager(self.data_dir_path)
        new_scene = scene_manager.new_scene(dataset_list)
        new_scene_hash = new_scene['sceneHash']

        loaded_dataset_dict = scene_manager.list_loaded_datasets(new_scene_hash)

        self.assertEqual(len(loaded_dataset_dict['loadedDatasets']), 1)

        add_datasets_list = ['just_fo', 'another_just_fo']
        dataset_list_success = ['just_fo', 'another_just_fo', 'just_fo', 'another_just_fo']
        success_dict = scene_manager.add_datasets(new_scene_hash, dataset_list_success)
        self.assertIsInstance(success_dict, dict)
        self.assertIn('sceneHash', success_dict)
        self.assertIn('href', success_dict)
        self.assertIn('addDatasetsSuccess', success_dict)
        self.assertNotIn('addDatasetsFail', success_dict)

        # Should contain both addDatasetsSuccess and addDatasetsFail
        dataset_list = ['just_fo']
        scene_manager = SceneManager(self.data_dir_path)
        new_scene = scene_manager.new_scene(dataset_list)
        new_scene_hash = new_scene['sceneHash']

        loaded_dataset_dict = scene_manager.list_loaded_datasets(new_scene_hash)

        self.assertEqual(len(loaded_dataset_dict['loadedDatasets']), 1)

        add_datasets_list = ['just_fo', 'another_just_fo']
        dataset_list_partial = ['no_such_thing', 'another_just_fo']
        partial_dict = scene_manager.add_datasets(new_scene_hash, dataset_list_partial)
        self.assertIsInstance(partial_dict, dict)
        self.assertIn('sceneHash', success_dict)
        self.assertIn('href', partial_dict)
        self.assertIn('addDatasetsSuccess', partial_dict)
        self.assertIn('addDatasetsFail', partial_dict)

        # Should contain both addDatasetsSuccess and addDatasetsFail
        dataset_list = ['just_fo']
        scene_manager = SceneManager(self.data_dir_path)
        new_scene = scene_manager.new_scene(dataset_list)
        new_scene_hash = new_scene['sceneHash']

        loaded_dataset_dict = scene_manager.list_loaded_datasets(new_scene_hash)

        self.assertEqual(len(loaded_dataset_dict['loadedDatasets']), 1)

        add_datasets_list = ['just_fo', 'another_just_fo']
        dataset_list_partial_not_just_string = ['no_such_thing', 'another_just_fo', 123]
        partial_dict_not_just_string = scene_manager.add_datasets(new_scene_hash, dataset_list_partial_not_just_string)
        self.assertIsInstance(partial_dict_not_just_string, dict)
        self.assertIn('sceneHash', success_dict)
        self.assertIn('href', partial_dict_not_just_string)
        self.assertIn('addDatasetsSuccess', partial_dict_not_just_string)
        self.assertIn('addDatasetsFail', partial_dict_not_just_string)

        # Just return None
        dataset_list = ['just_fo']
        scene_manager = SceneManager(self.data_dir_path)
        new_scene = scene_manager.new_scene(dataset_list)
        new_scene_hash = new_scene['sceneHash']

        loaded_dataset_dict = scene_manager.list_loaded_datasets(new_scene_hash)

        self.assertEqual(len(loaded_dataset_dict['loadedDatasets']), 1)

        dataset_list_fail = ['just_fo_', 'another_just_fo_']
        fail_return = scene_manager.add_datasets(new_scene_hash, dataset_list_fail)
        self.assertIsNone(fail_return)

        # Empty list should fail
        dataset_list = ['just_fo']
        scene_manager = SceneManager(self.data_dir_path)
        new_scene = scene_manager.new_scene(dataset_list)
        new_scene_hash = new_scene['sceneHash']

        loaded_dataset_dict = scene_manager.list_loaded_datasets(new_scene_hash)

        self.assertEqual(len(loaded_dataset_dict['loadedDatasets']), 1)

        empty_list = []
        with self.assertRaises(ValueError):
            scene_manager.add_datasets(new_scene_hash, empty_list)

        # String raises TypeError
        dataset_list = ['just_fo']
        scene_manager = SceneManager(self.data_dir_path)
        new_scene = scene_manager.new_scene(dataset_list)
        new_scene_hash = new_scene['sceneHash']

        loaded_dataset_dict = scene_manager.list_loaded_datasets(new_scene_hash)

        self.assertEqual(len(loaded_dataset_dict['loadedDatasets']), 1)

        just_a_string = 'just_fo'
        with self.assertRaises(TypeError):
            scene_manager.add_datasets(new_scene_hash, just_a_string)

    def test_list_loaded_datasets(self):
        """Return a list of loaded datasets in a scene

        """
        dataset_list = ['just_fo', 'another_just_fo']

        scene_manager = SceneManager(self.data_dir_path)
        new_scene = scene_manager.new_scene(dataset_list)
        new_scene_hash = new_scene['sceneHash']

        loaded_dataset_dict = scene_manager.list_loaded_datasets(new_scene_hash)

        self.assertIsInstance(loaded_dataset_dict, dict)
        self.assertIn('loadedDatasets', loaded_dataset_dict)
        self.assertIsInstance(loaded_dataset_dict['loadedDatasets'], list)

        self.assertEqual(len(loaded_dataset_dict['loadedDatasets']), 2)

        for dataset_meta in loaded_dataset_dict['loadedDatasets']:
            self.assertIsInstance(dataset_meta, dict)
            self.assertIn('datasetAlias', dataset_meta)
            self.assertIn('datasetHash', dataset_meta)
            self.assertIn('datasetHref', dataset_meta)
            self.assertIn('datasetName', dataset_meta)

        # Non-string raises TypeError
        with self.assertRaises(TypeError):
            scene_manager.list_loaded_datasets(1)

        # Invalid scene hash returns None
        scene_manager = SceneManager(self.data_dir_path)
        loaded_dataset_none = scene_manager.list_loaded_datasets('some_invalid_thing')
        self.assertIsNone(loaded_dataset_none)

    def test_delete_dataset(self):
        """Delete a dataset from a scene

        """
        dataset_list = ['just_fo', 'another_just_fo']

        scene_manager = SceneManager(self.data_dir_path)

        new_scene = scene_manager.new_scene(dataset_list)
        new_scene_hash = new_scene['sceneHash']

        active_scenes = scene_manager.list_scenes()['activeScenes']
        self.assertEqual(len(active_scenes), 1)

        loaded_dataset_dict = scene_manager.list_loaded_datasets(new_scene_hash)
        loaded_dataset_list = loaded_dataset_dict['loadedDatasets']

        self.assertEqual(len(loaded_dataset_list), 2)

        dataset_to_delete = loaded_dataset_list[0]['datasetHash']
        res = scene_manager.delete_loaded_dataset(new_scene_hash, dataset_to_delete)

        self.assertIsInstance(res, dict)
        self.assertIn('datasetDeleted', res)

        loaded_dataset_dict = scene_manager.list_loaded_datasets(new_scene_hash)
        loaded_dataset_list = loaded_dataset_dict['loadedDatasets']

        self.assertEqual(len(loaded_dataset_list), 1)

        # Delete the last dataset means deleting the scene
        dataset_to_delete = loaded_dataset_list[0]['datasetHash']
        res = scene_manager.delete_loaded_dataset(new_scene_hash, dataset_to_delete)

        self.assertIsNone(res)

        active_scenes = scene_manager.list_scenes()['activeScenes']
        self.assertEqual(len(active_scenes), 0)
        self.assertNotEqual(len(active_scenes), 1)

        # Set up the scene again
        scene_manager = SceneManager(self.data_dir_path)
        new_scene = scene_manager.new_scene(dataset_list)
        new_scene_hash = new_scene['sceneHash']
        loaded_dataset_dict = scene_manager.list_loaded_datasets(new_scene_hash)
        loaded_dataset_list = loaded_dataset_dict['loadedDatasets']
        dataset_to_delete = loaded_dataset_list[0]['datasetHash']

        # Non-string raises TypeError
        with self.assertRaises(TypeError):
            scene_manager.delete_loaded_dataset(1, dataset_to_delete)
        with self.assertRaises(TypeError):
            scene_manager.delete_loaded_dataset(new_scene_hash, 1)

        # Non existing scene, delete dataset
        non_ex_scene = scene_manager.delete_loaded_dataset('non_ex', dataset_to_delete)
        self.assertIsNone(non_ex_scene)

        # Delete non existing dataset
        non_ex_dataset = scene_manager.delete_loaded_dataset(new_scene_hash, 'non_ex')
        self.assertIsNone(non_ex_dataset)

    def test_list_loaded_dataset_information(self):
        """Get information about one dataset that is loaded into a scenes

        """
        # This data exists
        dataset_list = ['just_fo', 'another_just_fo']

        scene_manager = SceneManager(self.data_dir_path)
        new_scene = scene_manager.new_scene(dataset_list)
        scene_hash = new_scene['sceneHash']
        dataset_hash = new_scene['addDatasetsSuccess'][0]['datasetHash']

        dataset_info = scene_manager.list_loaded_dataset_info(
            scene_hash, dataset_hash)

        self.assertIsInstance(dataset_info, dict)
        self.assertIn('datasetName', dataset_info)
        self.assertIn('datasetHash', dataset_info)
        self.assertIn('datasetAlias', dataset_info)
        self.assertIn('datasetHref', dataset_info)

        # scene does not exist
        dataset_info = scene_manager.list_loaded_dataset_info(
            'scene_does_not_exist', dataset_hash)

        self.assertIsNone(dataset_info)

        # dataset does not exist
        dataset_info = scene_manager.list_loaded_dataset_info(
            scene_hash, 'dataset_does_not_exist')

        self.assertIsNone(dataset_info)

        # wrong argument types
        with self.assertRaises(TypeError):
            scene_manager.list_loaded_dataset_info(1, dataset_hash)
        with self.assertRaises(TypeError):
            scene_manager.list_loaded_dataset_info(scene_hash, 1)

    def test_dataset_orientation(self):
        """GET or PATCH dataset orientation

        """
        # This data exists
        dataset_list = ['just_fo']

        scene_manager = SceneManager(self.data_dir_path)
        new_scene = scene_manager.new_scene(dataset_list)  # dict
        scene_hash = new_scene['sceneHash']
        dataset_hash = scene_manager.list_loaded_datasets(scene_hash)['loadedDatasets'][0]['datasetHash']

        res = scene_manager.dataset_orientation(scene_hash, dataset_hash)

if __name__ == '__main__':
    """
    Testing as standalone program.
    """
    unittest.main(verbosity=2)
