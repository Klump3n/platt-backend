#!/usr/bin/env python3
"""
A testcase for /backend/scene_handler.py
"""

# Append the parent directory for importing the file.
import sys
sys.path.append('..')           # This contains scene_handler.py
from scene_handler import *     # Oh well...

import numpy as np
import unittest


class TestSimulationObject(unittest.TestCase):
    """
    Unittest for SimulationObject.
    """

    def setUp(self):
        self.example_object = SimulationObject('object name')

    def test_object_name_is_equal(self):
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
        testmatrix = np.asarray(
            [[ 1.,  2.,  3.,  4.],
             [ 0.,  1.1,  0.2,  0.1],
             [ -0.,  -1.,  -2.,  -3.],
             [ -1.1,  -.1,  0.,  1.]]
        )
        self.example_object.orientation(testmatrix)
        np.testing.assert_array_equal(
            self.example_object.orientation(), testmatrix)

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
        testmatrix = [
            [ 1.,  0.,  0.,  0.],
            [ 0.,  1.,  0.,  0.],
            [ 0.,  0.,  1.,  0.],
            [ 0.,  0.,  0.,  1.]
        ]
        with self.assertRaises(Exception):
            self.example_object.orientation(testmatrix)


if __name__ == '__main__':
    """
    Testing as standalone program.
    """
    unittest.main(verbosity=2)
