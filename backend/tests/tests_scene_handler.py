#!/usr/bin/env python3
"""
A testcase for backend.scenes_scene_prototype and
backend.scenes_object_prototype
"""

# NOTE: I am not really sure if it is beneficial to maintain a test suite on a
# one man project.

import os
import sys
import unittest
import pathlib
import numpy as np

# Append the parent directory for importing the file.
sys.path.append(os.path.join('..', '..'))  # Append the program root dir
from backend.scenes_scene_prototype import _ScenePrototype
from backend.scenes_object_prototype import _ObjectPrototype


class TestSimulationObject(unittest.TestCase):
    """
    Unittest for SimulationObject.
    """

    def setUp(self):
        # Instantiate the object
        test_path = pathlib.Path('this/is/a/test')
        self.example_object = _ObjectPrototype(test_path)

    def test_name_is_only_string(self):
        """
        Check if the object name can only be a string.
        """
        with self.assertRaises(TypeError):
            _ObjectPrototype(0)

    def test_object_name_is_equal(self):
        """
        Test if the object name equals the assigned name.
        """
        self.assertEqual(self.example_object.name(), 'test')

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
            [[1.,  2.,  3.,  4.],
             [0.,  1.1,  0.2,  0.1],
             [-0.,  -1.,  -2.,  -3.],
             [-1.1,  -.1,  0.,  1.]]
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
            [1.,  0.,  0.,  0.],
            [0.,  1.,  0.,  0.],
            [0.,  0.,  1.,  0.],
            [0.,  0.,  0.,  1.]
        ]
        with self.assertRaises(Exception):
            self.example_object.orientation(testlist)


class TestSimulationScene(unittest.TestCase):
    """
    Unittest for SimulationScene.
    """

    def setUp(self):
        # Instantiate the scene and add an object
        test_path = pathlib.Path('this/is/a/test')
        self.example_scene = _ScenePrototype(test_path)

    # These tests do not work right now, I kind of know why but I also think
    # that I should have documented their purpose waaaaay better.

    # def test_scene_metadata(self):
    #     """
    #     Test if the scene metadata is as expected.
    #     """

    #     metadata = self.example_scene.metadata()
    #     self.assertIs(type(metadata), dict)
    #     self.assertTrue('name' in metadata)

    # def test_object_is_instance_of_SimulationObject(self):
    #     """
    #     Check if the object is an instance of the object class.
    #     """

    #     self.assertIsInstance(
    #         self.example_scene.objects().get('example object'),
    #         _ObjectPrototype
    #     )


if __name__ == '__main__':
    """
    Testing as standalone program.
    """
    unittest.main(verbosity=2)
