#!/usr/bin/env python3

"""
An instance for an empty scene.
"""

import numpy as np
import unittest


class SimulationObject:
    """
    Prototype for an object.
    Holds geometrical data, orientation, etc.
    """

    def __init__(self, name=None):
        """
        Initialise an object.
        """
        self.object_name = name
        self.view_matrix = np.eye(4)  # 4D identity matrix
        self.index_data_list = []
        self.tetraeder_data_list = []
        self.wireframe_data_list = []

    def __del__(self):
        """
        Delete an object.
        """

        # Maybe do something with the space that is occupied by the tets or
        # smth.. Like reorganise the arrays.
        pass

    def name(self, data=None):
        """
        Get or set the name of the object.
        """

        if data is not None:
            self.object_name = data

        return self.object_name

    def orientation(self, view_matrix=None):
        """
        Get (if modelViewMatrix == None) or set (if modelViewMatrix not == None)
        the orientation of an object in the scene.
        """

        if view_matrix is not None:

            # Check for numpy array and 4x4 shape for the view_matrix.
            is_np_array = (type(view_matrix) is np.ndarray)
            is_4x4 = (view_matrix.shape == self.view_matrix.shape)

            if not is_np_array:
                raise Exception('view_matrix is wrong type')
            if not is_4x4:
                raise Exception('view_matrix is not 4x4')


            try:
                self.view_matrix = view_matrix
            except:
                raise Exception('something happened while trying to set the '+
                                'view_matrix')

        return self.view_matrix

    def index_data(self, data=None):
        """
        Get or set the index data.
        """

        if data is not None:
            self.index_data_list = data

        return self.index_data_list

    def tetraeder_data(self, data=None):
        """
        Get or set the tetraeder data.
        """

        if data is not None:
            self.tetraeder_data_list = data

        return self.tetraeder_data_list

    def wireframe_data(self, data=None):
        """
        Get or set the wireframe data.
        """

        if data is None:
            self.wireframe_data_list = data

        return self.wireframe_data_list


class SimulationScene:
    """
    Holds all the objects in a scene and also the meta data.
    """

    def __init__(self):
        """
        Initialise an empty scene.
        """
        self.object_list = []   # Better use dictionaries?

    def __del__(self):
        """
        Delete the scene.
        """
        pass

    def objects(self, add=None, remove=None):
        """
        Add and/or remove an object to/from the scene.
        """

        if add is not None:
            self.object_list.append(add)

        if remove is not None:
            self.object_list.pop(remove)

        return self.object_list

    def metadata(self):
        """
        Get the metadata for the scene.
        """
        pass

