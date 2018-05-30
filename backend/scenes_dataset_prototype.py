#!/usr/bin/env python3
"""
The class for a dataset.

a dataset is all data we have about some simulation. That contains the name,
all the data points, its orientation in R3 and so on.

"""
import os
import numpy as np

from backend.util.timestamp_to_sha1 import timestamp_to_sha1
import backend.dataset_parser as dp


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
        self._selected_orientation = {
            'datasetOrientation': {
                'datasetTranslation': [],
                'datasetRotation': []
            },
            'datasetOrientationInit': False
        }

        self._selected_timestep = ''  # String

        self._selected_field = {
            'type': '__no_type__',
            'name': '__no_field__'
        }

        self._hash_dict = {
            'mesh': None,
            'field': None
        }

        self._index_data_list = []
        self._tetraeder_data_list = []
        self._wireframe_data_list = []
        self._timestep_data_list = []

        self._fields = {}
        self._meshes = {}

        # initialize the mesh parser
        self._mp = dp.ParseDataset(self.dataset_path)

        # for init: find the lowest timestep and set it
        lowest_timestep = self.timestep_list()[0]
        self.timestep(set_timestep=lowest_timestep)

    def meta(self):
        """
        Returns the meta information dictionary.

        Returns:
         dict: The meta information dict.

        """
        return self.dataset_meta_dict

    def hashes(self):
        """
        Returns a dictionary with the hashes for the field and the geometry of
        the dataset.

        Returns:
         dict: The hashes in a dictionary.

        """
        return self._hash_dict

    def websocket_payload(self):
        """
        Return a dictionary with relevant data about the new state of the
        dataset.

        """
        return {
            'datasetHash': self.dataset_sha1,
            'update': 'mesh',
            'hashes': self.hashes(),
            'field_type': self._selected_field['type']
        }

    def orientation(self, set_orientation=None):
        """
        Get (if set_orientation is None) or set (if set_orientation is not None)
        the orientation of a dataset in the scene.

        The index mapping is as follows:
        [
        0, 4, 8,  12,
        1, 5, 9,  13,
        2, 6, 10, 14,
        3, 7, 11, 15
        ]

        Args:
         set_orientation (list or None, optional, defaults to None): A 16-tuple
          for setting the orientation of the dataset. The top-left 3x3 matrix
          should be unitary, so rotation is represented. The rest can contain
          scaling values.

        Raises:
         TypeError: If ``type(set_orientation)`` is not None or list.
         ValueError: If the lenght of ``set_orientation`` is not 16.

        """
        if set_orientation is not None:
            self._selected_orientation['datasetOrientation'] = set_orientation

            if self._selected_orientation['datasetOrientationInit'] is False:
                self._selected_orientation['datasetOrientationInit'] = True

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

            hash_dict = {
                'mesh': list(self._meshes.keys()),
                'field': list(self._fields.keys())
            }

            mp_data = self._mp.timestep_data(
                self._selected_timestep, self._selected_field, hash_dict=hash_dict)

            mp_data_mesh_hash = mp_data['hash_dict']['mesh']
            mp_data_field_hash = mp_data['hash_dict']['field']

            self._hash_dict['mesh'] = mp_data_mesh_hash
            self._hash_dict['field'] = mp_data_field_hash

            if mp_data_mesh_hash not in hash_dict['mesh']:
                self._meshes['current'] = {
                    'mesh_hash': mp_data['hash_dict']['mesh'],
                    'nodes': mp_data['nodes']['data'],
                    'nodes_center': mp_data['nodes_center'],
                    'tets': mp_data['tets']['data'],
                    'wireframe': mp_data['wireframe']['data'],
                    'free_edges': mp_data['free_edges']['data']
                }

                self._meshes[mp_data['hash_dict']['mesh']] = self._meshes['current']

            else:
                self._meshes['current'] = self._meshes[mp_data_mesh_hash]

            if mp_data_field_hash not in hash_dict['field']:
                self._fields['current'] = {
                    'field_hash': mp_data['hash_dict']['field'],
                    'field': mp_data['field']['data']
                }

                self._fields[mp_data['hash_dict']['field']] = self._fields['current']

            else:
                self._fields['current'] = self._fields[mp_data_field_hash]

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
            elemental_fields.append(field.stem)  # just append the file name

        # cut the element type from the field name
        try:
            elemental_fields = [
                field.rsplit('.', 1) for field in elemental_fields
            ]
            elemental_fields = sorted(
                np.unique(np.asarray(elemental_fields)[:, 0])
            )
        except IndexError:
            pass

        nodal_fields = []
        nodal_field_dir = timestep_dir / 'no'
        nodal_field_paths = sorted(nodal_field_dir.glob('*.bin'))
        for field in nodal_field_paths:
            nodal_fields.append(field.stem)  # just append the file name

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
        # get a list of fields we can display for this timestep
        fields = self.field_dict()
        elemental_fields = fields['elemental']
        nodal_fields = fields['nodal']

        if set_field is not None:
            set_field_type = set_field['type']
            set_field_name = set_field['name']

            # Initialise
            mp_data = None

            hash_dict = {
                'mesh': list(self._meshes.keys()),
                'field': list(self._fields.keys())
            }

            # see if the field we want to set is available...
            if (
                    (set_field_type == 'nodal' and
                     set_field_name in nodal_fields)
                    or
                    (set_field_type == 'elemental' and
                     set_field_name in elemental_fields)
            ):
                self._selected_field = set_field

                mp_data = self._mp.timestep_data(
                    self._selected_timestep,
                    self._selected_field,
                    hash_dict=hash_dict
                )

            if (
                    set_field_type == '__no_type__' or
                    set_field_name == '__no_field__'
            ):
                self._selected_field = set_field

                mp_data = self._mp.timestep_data(
                    self._selected_timestep,
                    field=None,
                    hash_dict=hash_dict
                )

            # update the current data
            if mp_data is not None:
                mp_data_mesh_hash = mp_data['hash_dict']['mesh']
                mp_data_field_hash = mp_data['hash_dict']['field']

                self._hash_dict['mesh'] = mp_data_mesh_hash
                self._hash_dict['field'] = mp_data_field_hash

                if mp_data_mesh_hash not in hash_dict['mesh']:
                    self._meshes['current'] = {
                        'mesh_hash': mp_data['hash_dict']['mesh'],
                        'nodes': mp_data['nodes']['data'],
                        'nodes_center': mp_data['nodes_center'],
                        'tets': mp_data['tets']['data'],
                        'wireframe': mp_data['wireframe']['data'],
                        'free_edges': mp_data['free_edges']['data']
                    }

                    self._meshes[mp_data['hash_dict']['mesh']] = self._meshes['current']

                else:
                    self._meshes['current'] = self._meshes[mp_data_mesh_hash]

                if mp_data_field_hash not in hash_dict['field']:
                    self._fields['current'] = {
                        'field_hash': mp_data['hash_dict']['field'],
                        'field': mp_data['field']['data']
                    }

                    self._fields[mp_data['hash_dict']['field']] = self._fields['current']

                else:
                    self._fields['current'] = self._fields[mp_data_field_hash]

        return self._selected_field

    def surface_mesh(self, current_mesh_hash=None):
        """
        Get surface mesh data.

        """
        if (
                (current_mesh_hash is None) or
                (current_mesh_hash != self._meshes['mesh_hash'])
        ):
            return self._meshes['current']
        else:
            return {
                'mesh_hash': None,
                'nodes': [],
                'nodes_center': [],
                'tets': [],
                'wireframe': [],
                'free_edges': []
            }

    def surface_field(self, current_field_hash=None):
        """
        Returns the field values for the surface mesh.

        """
        if (
                (current_field_hash is None) or
                (current_field_hash != self._fields['field_hash'])
        ):
            return self._fields['current']
        else:
            return {
                'field_hash': None,
                'field': []
            }

    def surface_field_min_max(self):
        """
        Returns the min and max values of the currently set field.

        """
        current_field = self._fields['current']['field']
        current_min = np.floor(np.min(current_field)) - 1
        current_max = np.ceil(np.max(current_field)) + 1
        # if current_max == current_min:
        #     current_min = current_min - 1
        #     current_max = current_max + 1

        return {
            'fieldMin': current_min,
            'fieldMax': current_max
        }
