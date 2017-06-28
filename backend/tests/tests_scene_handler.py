#!/usr/bin/env python3
"""
A testcase for /backend/scene_handler.py
"""

import sys
import unittest
import numpy as np

# Append the parent directory for importing the file.

sys.path.append('../..')            # Append the program root dir
from backend.scene_handler import *     # Oh well...


class TestSimulationObject(unittest.TestCase):
    """
    Unittest for SimulationObject.
    """

    def setUp(self):
        # Instantiate the object
        self.example_object = SimulationObject('object name')

    def test_name_is_only_string(self):
        """
        Check if the object name can only be a string.
        """
        with self.assertRaises(TypeError):
            SimulationObject(0)

    def test_object_name_is_equal(self):
        """
        Test if the object name equals the assigned name.
        """
        self.assertEqual(self.example_object.name(), 'object name')

    def test_default_orientation_is_unitary(self):
        """
        Check if the default transformation matrix is a 4x4 unit matrix.
        """
        np.testing.assert_array_equal(
            self.example_object.orientation(), np.eye(4))

    def test_set_orientation(self):
        """
        Set the transformation matrix to something other than the unitary
        matrix.
        """
        nparray = np.asarray(
            [[ 1.,  2.,  3.,  4.],
             [ 0.,  1.1,  0.2,  0.1],
             [ -0.,  -1.,  -2.,  -3.],
             [ -1.1,  -.1,  0.,  1.]]
        )
        self.example_object.orientation(nparray)
        np.testing.assert_array_equal(
            self.example_object.orientation(), nparray)

    def test_set_orientation_with_non_4x4_transform_exception(self):
        """
        Check wether the orientation does not accept np arrays other that 4x4.
        """
        testmatrix = np.eye(3)
        with self.assertRaises(Exception):
            self.example_object.orientation(testmatrix)

    def test_set_orientation_with_non_numpy_array_exception(self):
        """
        See that anything but a numpy array raises an exception.
        """
        testlist = [
            [ 1.,  0.,  0.,  0.],
            [ 0.,  1.,  0.,  0.],
            [ 0.,  0.,  1.,  0.],
            [ 0.,  0.,  0.,  1.]
        ]
        with self.assertRaises(Exception):
            self.example_object.orientation(testlist)

class TestSimulationScene(unittest.TestCase):
    """
    Unittest for SimulationScene.
    """

    def setUp(self):
        # Instantiate the scene and add an object
        self.example_scene = SimulationScene('scene name')
        self.example_scene.objects(add='example object')

    def test_scene_metadata(self):
        """
        Test if the scene metadata is as expected.
        """

        metadata = self.example_scene.metadata()
        self.assertIs(type(metadata), dict)
        self.assertTrue('name' in metadata)

    def test_object_is_instance_of_SimulationObject(self):
        """
        Check if the object is an instance of the object class.
        """

        self.assertIsInstance(
            self.example_scene.objects().get('example object'),
            SimulationObject
        )

if __name__ == '__main__':
    """
    Testing as standalone program.
    """
    unittest.main(verbosity=2)
