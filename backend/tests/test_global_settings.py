#!/usr/bin/env python3
"""
Test the global_settings

"""
import os
import sys
import unittest
import pathlib

# Append the parent directory for importing the file.
sys.path.append(os.path.join('..', '..'))  # Append the program root dir
import backend.global_settings as gloset
from backend.scenes_manager import SceneManager


class Test_global_settings(unittest.TestCase):
    """
    Test the API.

    """

    def setUp(self):
        file_path = os.path.dirname(__file__)
        self.data_dir_string = 'mock_data'
        self.data_dir_path = pathlib.Path('{}/{}'.format(
            file_path, self.data_dir_string))


    def test_init(self):
        """Init global settings

        """
        gloset.init(self.data_dir_path)

        self.assertIsInstance(gloset.scene_manager, SceneManager)

        # # Something other that os.pathlike raises a TypeError
        # with self.assertRaises(TypeError):
        #     gloset.init('some_string')
