#!/usr/bin/env python3
"""
Tests for backend.scenes_object_prototype

"""
import unittest
import pathlib

# Append the parent directory for importing the file.
import sys
import os
sys.path.append(os.path.join('..', '..'))  # Append the program root dir
from backend.scenes_object_prototype import _ObjectPrototype


class Test_ObjectPrototype(unittest.TestCase):

    def setUp(self):
        # Set the path to a mock dataset
        self.valid_path = pathlib.Path('test_ObjectPrototype')
        self.test_path = pathlib.Path('this/is/a/test')
        self.example_object = _ObjectPrototype(self.test_path)

    def test_instance(self):
        """
        Check if the object instantiates.

        """
        example_object = _ObjectPrototype(self.test_path)
        self.assertIsInstance(self.example_object, _ObjectPrototype)

if __name__ == '__main__':
    """
    Testing as standalone program.
    """
    unittest.main(verbosity=2)
