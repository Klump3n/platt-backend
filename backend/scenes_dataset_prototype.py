#!/usr/bin/env python3
"""
The class for a dataset.

a dataset is all data we have about some simulation. That contains the name,
all the data points, its orientation in R3 and so on.

"""
import os

from backend.util.timestamp_to_sha1 import timestamp_to_sha1
import backend.data_backend as data_backend


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

        # Save the dataset path
        self.dataset_path = dataset_path.absolute()

        # Grab the last entry from the path
        self.dataset_name = self.dataset_path.absolute().name

        # Generate the SHA1 on dataset object creation
        self.dataset_sha1 = timestamp_to_sha1()

        self.dataset_meta_dict = {
            'datasetName': self.dataset_name,
            'datasetHash': self.dataset_sha1,
            'datasetAlias': '',
            'datasetHref': ''
        }

        # Init
        self._selected_orientation = [
            1, 0, 0, 0,
            0, 1, 0, 0,
            0, 0, 1, 0,
            0, 0, 0, 1
        ]                           # List
        self._selected_timestep = ''  # String
        self._selected_field = ''

        self._index_data_list = []
        self._tetraeder_data_list = []
        self._wireframe_data_list = []

        # Find the lowest timestep and set it
        lowest_timestep = self.timestep_list()[0]
        self.timestep(set_timestep=lowest_timestep)

        # demo for andreas
        # tests dont cover this, this breaks a lot of stuff
        #
        # convert to string paths
        nodes = str(self.dataset_path / 'fo' / lowest_timestep / 'nodes.bin')
        elements = str(self.dataset_path / 'fo' / lowest_timestep / 'elements.dc3d8.bin')
        print(nodes, elements)
        # init mesher
        mesher = data_backend.UnpackMesh(node_path=nodes, element_path=elements)
        self._tetraeder_data_list = mesher.return_unique_surface_nodes()
        self._index_data_list = mesher.return_surface_indices()

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

            self._selected_orientation = view_matrix

        return self._selected_orientation

    def timestep_list(self):
        """
        Get a sorted list of all the timesteps for a dataset.

        Args:
         None: No args.

        Returns:
         list: A sorted list with all timesteps in the dataset.

        Todo:
         Make this more resilient against non exising directories via try
         except.

        """
        dataset_dir = self.dataset_path / 'fo'
        dirs = sorted(dataset_dir.glob('*/'))  # Glob all directories

        timestep_list = []
        for path in dirs:
            timestep_list.append(path.name)

        return timestep_list

    def timestep(self, set_timestep=None):
        """
        GET or PATCH the currently set timestep for this dataset.

        Args:
         set_timestep (str or None): None if we want to get the current timestep,
          otherwise the timestep we want to set.

        Returns:
         str or None: The currently set timestep or None if the timestep could
         not be set.

        """
        if set_timestep is not None:
            if not isinstance(set_timestep, str):
                raise TypeError('set_timestep is {}, expected str'.format(
                    type(set_timestep).__name__))

            if set_timestep not in self.timestep_list():
                return self._selected_timestep

            self._selected_timestep = set_timestep

        return self._selected_timestep

    def field_dict(self):
        """
        Get a list of fields for the selected timestep.

        Args:
         None: No args.

        Returns:
         dict: A dict with two lists of fields, one for elemental and one for
         nodal fields.

        Todo:
         Make this more resilient against non exising directories via try
         except.

        """
        timestep_dir = self.dataset_path / 'fo' / self._selected_timestep

        elemental_fields = []
        elemental_field_dir = timestep_dir / 'eo'
        elemental_field_paths = sorted(elemental_field_dir.glob('*.bin'))
        for field in elemental_field_paths:
            elemental_fields.append(field.stem)

        nodal_fields = []
        nodal_field_dir = timestep_dir / 'no'
        nodal_field_paths = sorted(nodal_field_dir.glob('*.bin'))
        for field in nodal_field_paths:
            nodal_fields.append(field.stem)

        return_dict = {
            'elemental': elemental_fields,
            'nodal': nodal_fields
        }

        return return_dict

    def field(self, set_field=None):
        """
        GET or PATCH (set) the available fields for the selected timestep in
        the dataset.

        Args:
         set_field (str or None): None if we want to get the current field,
          otherwise the field we want to set.

        """
        if set_field is not None:
            if not isinstance(set_field, str):
                raise TypeError('set_field is {}, expected None or str'.format(
                    type(set_field).__name__))

        # get a list of fields we can display for this timestep
        fields = self.field_dict()
        elemental_fields = fields['elemental']
        nodal_fields = fields['nodal']

        if set_field is not None:
            # see if the field we want to set is available...
            if (
                    set_field not in elemental_fields and
                    set_field not in nodal_fields
            ):
                # ..., if not return 'no_field'
                return 'no_field'

            # if it is we can set it
            self._selected_field = set_field

        else:
            # see if the field we want to get is available...
            if (
                    self._selected_field not in elemental_fields and
                    self._selected_field not in nodal_fields
            ):
                # ..., if not return 'no_field'
                return 'no_field'

        return self._selected_field

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

    #         is_4x4 = (view_matrix.shape == self._selected_orientation.shape)
    #         if not is_4x4:
    #             raise ValueError('view_matrix is not 4x4')

    #         try:
    #             self._selected_orientation = view_matrix
    #         except:
    #             raise BaseException('something happened while trying to set ' +
    #                             'the view_matrix')

    #     return self._selected_orientation

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
