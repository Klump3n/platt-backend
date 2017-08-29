#!/usr/bin/env python3

import os
import numpy as np


class _ObjectPrototype:
    """
    Prototype for an object.
    Holds geometrical data, orientation, etc.
    """

    def __init__(self, object_path):
        """
        Initialise an object. We expect the path to some simulation data as an
        input.
        """

        if not isinstance(object_path, os.PathLike):
            raise TypeError(
                'object_path is {}, expected os.PathLike'.format(
                    type(object_path).__name__))

        # Grab the last entry from the path
        self._object_name = object_path.absolute().name

        self._view_matrix = np.eye(4)  # 4D identity matrix
        self._index_data_list = []
        self._tetraeder_data_list = []
        self._wireframe_data_list = []

    def name(self):
        """
        Get the name of the object.
        """

        return self._object_name

    def orientation(self, view_matrix=None):
        """
        Get (if view_matrix is None) or set (if view_matrix is not None)
        the orientation of an object in the scene.
        """

        if view_matrix is not None:

            # Check for numpy array and 4x4 shape for the view_matrix.
            is_np_array = (isinstance(view_matrix, np.ndarray))
            is_4x4 = (view_matrix.shape == self._view_matrix.shape)

            if not is_np_array:
                raise TypeError('view_matrix is wrong type')
            if not is_4x4:
                raise TypeError('view_matrix is not 4x4')

            try:
                self._view_matrix = view_matrix
            except:
                raise Exception(
                    'something happened while trying to set the view_matrix')

        return self._view_matrix

    def index_data(self, data=None):
        """
        Get or set the index data.
        """

        if data is not None:
            self._index_data_list = data

        return self._index_data_list

    def tetraeder_data(self, data=None):
        """
        Get or set the tetraeder data.
        """

        if data is not None:
            self._tetraeder_data_list = data

        return self._tetraeder_data_list

    def wireframe_data(self, data=None):
        """
        Get or set the wireframe data.
        """

        if data is None:
            self._wireframe_data_list = data

        return self._wireframe_data_list
