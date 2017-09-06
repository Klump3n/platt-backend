#!/usr/bin/env python3
"""
The class for an object.

An object is all data we have about some simulation. That contains the name,
all the data points, its orientation in R3 and so on.

"""
import os
import numpy as np


class _ObjectPrototype:
    """
    The prototype class for a simulation object.

    On initialization the name of the object is set based on the path to the
    data. The initial orientation is set to an identity transformation and all
    the lists for containing data points are initialized.

    Args:
     object_path (`os.PathLike`): The path to some simulation data.

    Raises:
     TypeError: If `object_path` is not `os.PathLike`

    Todo:
     Load all the simulation data on initialization.

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

        Returns:
         str: The name of the object.

        """
        return self._object_name

    def orientation(self, view_matrix=None):
        """
        Get (if view_matrix is None) or set (if view_matrix is not None)
        the orientation of an object in the scene.

        Args:
         view_matrix (np.ndarray or None, optional, defaults to None): A 4x4
          numpy matrix for setting the orientation of the object. The top-left
          3x3 matrix should be unitary, so rotation is represented. The rest
          can contain scaling values.

        Raises:
         TypeError: If ``type(view_matrix)`` is not None or np.ndarray and/or
          if the shape is not 4x4.

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
                raise Exception('something happened while trying to set the ' +
                                'view_matrix')

        return self._view_matrix

    def index_data(self, data=None):
        """
        Get or set the index data.

        Todo:
         Everything about this. This is just a placeholder for now. We need to
         implement methods for doing this automatically. This should call a
         method for extracting index data.

        """
        if data is not None:
            self._index_data_list = data

        return self._index_data_list

    def tetraeder_data(self, data=None):
        """
        Get or set the tetraeder data.

        Todo:
         Everything about this. This is just a placeholder for now. We need to
         implement methods for doing this automatically. This should call a
         method for extracting tetraeder data.

        """
        if data is not None:
            self._tetraeder_data_list = data

        return self._tetraeder_data_list

    def wireframe_data(self, data=None):
        """
        Get or set the wireframe data.

        Todo:
         Everything about this. This is just a placeholder for now. We need to
         implement methods for doing this automatically. This should call a
         method for extracting wireframe data.

        """

        if data is None:
            self._wireframe_data_list = data

        return self._wireframe_data_list
