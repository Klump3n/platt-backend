#!/usr/bin/env python3
"""
A testcase for backend.scenes_scene_prototype and
backend.scenes_object_prototype
"""
import os
import sys
import unittest
import pathlib
import numpy as np

# Append the parent directory for importing the file.
sys.path.append(os.path.join('..', '..'))  # Append the program root dir
from backend.scenes_scene_prototype import _ScenePrototype
from backend.scenes_dataset_prototype import _DatasetPrototype


class TestSimulationObject(unittest.TestCase):
    """
    Unittest for SimulationObject.
    """
    pass


if __name__ == '__main__':
    """
    Testing as standalone program.
    """
    unittest.main(verbosity=2)
