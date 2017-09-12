#!/usr/bin/env python3
"""
Tests for backend.scenes_object_prototype

"""
import unittest
import path

# Append the parent directory for importing the file.
sys.path.append(os.path.join('..', '..'))  # Append the program root dir
from backend.scenes_object_prototype import _ObjectPrototype


class TestSimulationObject(unittest.TestCase):

    def setUp(self):
        # Set the path to a mock dataset
        self.test_path = pathlib.Path('this/is/a/test')
        self.example_object = _ObjectPrototype(test_path)

    def test_instance(self):
        """
        Check if the object instantiates.

        """
        example_object = _ObjectPrototype(test_path)
        self.assertIsInstance(self.example_object)
