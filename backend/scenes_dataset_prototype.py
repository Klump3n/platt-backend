#!/usr/bin/env python3
"""
The class for a dataset.

a dataset is all data we have about some simulation. That contains the name,
all the data points, its orientation in R3 and so on.

"""
import os
import numpy as np

from backend.util.timestamp_to_sha1 import timestamp_to_sha1


class _DatasetPrototype:
    """
    The prototype class for a simulation dataset.

    On initialization the name of the dataset is set based on the path to the
    data. The initial orientation is set to an identity transformation and all
    the lists for containing data points are initialized.

    Args:
     dataset_path (`os.PathLike`): The path to some simulation data.

    Raises:
     TypeError: If `dataset_path` is not `os.PathLike`
     ValueError: If `dataset_path` does not exist.

    Todo:
     Load all the simulation data on initialization.

    """
    def __init__(self, dataset_path):
        """
        Initialise a dataset. We expect the path to some simulation data as an
        input.

        """
        if not isinstance(dataset_path, os.PathLike):
            raise TypeError(
                'dataset_path is {}, expected os.PathLike'.format(
                    type(dataset_path).__name__))

        # Check if the path exists
        if not dataset_path.exists():
            raise ValueError(
                '{} does not exist'.format(dataset_path.absolute()))

        # Grab the last entry from the path
        dataset_name = dataset_path.absolute().name

        # Generate the SHA1 on dataset object creation
        dataset_sha1 = timestamp_to_sha1()

        self.dataset_meta_dict = {
            'datasetName': dataset_name,
            'datasetHash': dataset_sha1,
            'datasetAlias': '',
            'datasetHref': ''
        }

        self._view_matrix = [
            1, 0, 0, 0,
            0, 1, 0, 0,
            0, 0, 1, 0,
            0, 0, 0, 1
        ]
        # self._view_matrix = np.eye(4)  # 4D identity matrix
        self._index_data_list = []
        self._tetraeder_data_list = []
        self._wireframe_data_list = []

    def meta(self):
        """
        Returns the meta information dictionary.

        Returns:
         dict: The meta information dict.

        """
        return self.dataset_meta_dict

    def orientation(self, view_matrix=None):
        """
        Get (if view_matrix is None) or set (if view_matrix is not None)
        the orientation of a dataset in the scene.

        The index mapping is as follows:
        [
        0, 4, 8,  12,
        1, 5, 9,  13,
        2, 6, 10, 14,
        3, 7, 11, 15
        ]

        Args:
         view_matrix (list or None, optional, defaults to None): A 16-tuple
          for setting the orientation of the dataset. The top-left 3x3 matrix
          should be unitary, so rotation is represented. The rest can contain
          scaling values.

        Raises:
         TypeError: If ``type(view_matrix)`` is not None or list.
         ValueError: If the lenght of ``view_matrix`` is not 16.

        """
        if view_matrix is not None:
            if not isinstance(view_matrix, list):
                raise TypeError('view_matrix is {}, expected list'.format(
                        type(view_matrix).__name__))

            if not len(view_matrix) == 16:
                raise ValueError('len(view_matrix) must be 16')

            self._view_matrix = view_matrix

        return self._view_matrix

    # def orientation(self, view_matrix=None):
    #     """
    #     Get (if view_matrix is None) or set (if view_matrix is not None)
    #     the orientation of a dataset in the scene.

    #     Args:
    #      view_matrix (np.ndarray or None, optional, defaults to None): A 4x4
    #       numpy matrix for setting the orientation of the dataset. The top-left
    #       3x3 matrix should be unitary, so rotation is represented. The rest
    #       can contain scaling values.

    #     Raises:
    #      TypeError: If ``type(view_matrix)`` is not None or np.ndarray.
    #      ValueError: If the shape of ``view_matrix`` is not 4x4.

    #     """
    #     if view_matrix is not None:
    #         # Check for numpy array and 4x4 shape for the view_matrix.
    #         is_np_array = (isinstance(view_matrix, np.ndarray))
    #         if not is_np_array:
    #             raise TypeError('view_matrix is wrong type')

    #         is_4x4 = (view_matrix.shape == self._view_matrix.shape)
    #         if not is_4x4:
    #             raise ValueError('view_matrix is not 4x4')

    #         try:
    #             self._view_matrix = view_matrix
    #         except:
    #             raise BaseException('something happened while trying to set ' +
    #                             'the view_matrix')

    #     return self._view_matrix

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
