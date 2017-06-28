#!/usr/bin/env python3

"""
An instance for an empty scene.
"""

import numpy as np

class SimulationObject:
    """
    Prototype for an object.
    Holds geometrical data, orientation, etc.
    """

    def __init__(self, name):
        """
        Initialise an object.
        """

        if type(name) is not str:
            raise TypeError('name must be str')
        self._object_name = name

        self._view_matrix = np.eye(4)  # 4D identity matrix
        self._index_data_list = []
        self._tetraeder_data_list = []
        self._wireframe_data_list = []

    def __del__(self):
        """
        Delete an object.
        """

        # Maybe do something with the space that is occupied by the tets or
        # smth.. Like reorganise the arrays.
        pass

    def name(self):
        """
        Get or set the name of the object.
        """

        return self._object_name

    def orientation(self, view_matrix=None):
        """
        Get (if modelViewMatrix == None) or set (if modelViewMatrix not == None)
        the orientation of an object in the scene.
        """

        if view_matrix is not None:

            # Check for numpy array and 4x4 shape for the view_matrix.
            is_np_array = (type(view_matrix) is np.ndarray)
            is_4x4 = (view_matrix.shape == self._view_matrix.shape)

            if not is_np_array:
                raise Exception('view_matrix is wrong type')
            if not is_4x4:
                raise Exception('view_matrix is not 4x4')


            try:
                self._view_matrix = view_matrix
            except:
                raise Exception('something happened while trying to set the '+
                                'view_matrix')

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


class SimulationScene:
    """
    Holds all the objects in a scene and also the meta data.
    """

    def __init__(self, name):
        """
        Initialise an empty scene.
        """

        self._scene_name = name
        self._object_list = {}

    def __del__(self):
        """
        Delete the scene.
        """
        pass

    def objects(self, add=None, remove=None):
        """
        Add and/or remove an object to/from the scene.
        """

        # Add an object
        if add is not None:
            if not add in self._object_list:
                new_object = SimulationObject(add)
                self._object_list[add] = new_object
            else:
                print('Object already present in scene.')

        # Remove an object
        if remove is not None:
            try:
                self._object_list.pop(remove)
            except:
                print('No such object in scene.')

        return self._object_list

    def metadata(self, name=None):
        """
        Set or get the metadata for the scene.
        """

        if name is not None:
            self._scene_name = name

        return {
            'name': self._scene_name
        }


if __name__ == '__main__':
    SimulationObject(12)
    scene = SimulationScene('asdf')
    objects = scene.objects(add='asdf')
    print(type(objects.get('asdf')))
