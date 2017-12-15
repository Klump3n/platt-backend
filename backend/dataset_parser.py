#!/usr/bin/env python3
"""
An implementation of a dataset parser.

"""
import os
import re
import struct
import hashlib
import numpy as np

import backend.binary_formats as binary_formats
import backend.dataset_mangler as dm


class ParseDataset:
    """
    Unpack and store data for a dataset.

    """
    def __init__(self, dataset_dir):
        """
        Initialize the parser.

        Args:
         dataset_dir (os.PathLike): The dataset directory that contains all
          the information about the dataset.

        Raises:
         TypeError: If ``type(dataset_dir)`` is not `os.PathLike`.

        """
        if not isinstance(dataset_dir, os.PathLike):
            raise TypeError('dataset_dir is {}, expected os.PathLike'.format(
                type(dataset_dir).__name__))

        self.dataset_dir = dataset_dir
        self.fo_dir = self.dataset_dir / 'fo'

        self.field_map = None
        self._surface_node_count = None

    def _file_hash(self, file_path):
        """
        Return a SHA1 hash for a file.

        """
        if not file_path.exists():
            return None
            # raise ValueError('{} does not exist'.format(str(file_path)))

        checksum = hashlib.sha1()

        with open(file_path, 'rb') as open_file:
            file_contents = open_file.read(65536)  # read 64kB
            while file_contents:
                checksum.update(file_contents)
                file_contents = open_file.read(65536)  # read 64kB

        return checksum.hexdigest()

    def _read_binary_data(self, binary_file, fmt):
        """
        Return the data that was read from the binary file at path.

        fmt is a dict, containing
         data_point_size (int): The number of bytes per data point
         data_point_type (str): The data type (d = double, i = integer)
         points_per_unit (int): The number of data points that belong together.

        Args:
         binary_file (os.PathLike): The file from which we want to read binary
          data.
         fmt (dict): A dictionary containing the number of bytes per
          data point, the format of the data point (int, double, ...) and the
          number of data points that make up a unit (see above).

        Returns:
         list: The data we read.

        Raises:
         TypeError: If ``type(binary_file)`` is not `os.PathLike`.
         TypeError: If ``type(fmt)`` is not `dict`.
         ValueError: If ``binary_file`` does not exist.

        """
        # let this just raise a KeyError if we hand it a wrong dict
        data_point_size = fmt['data_point_size']
        data_point_type = fmt['data_point_type']
        points_per_unit = fmt['points_per_unit']

        # read binary from file
        with open(binary_file, 'rb') as open_binary_file:
            bin_data = open_binary_file.read()

        bin_data_points = int(len(bin_data) / data_point_size)

        # little endian
        struct_format = '<{}{}'.format(bin_data_points, data_point_type)

        data = struct.unpack(struct_format, bin_data)
        data = np.asarray(data)

        # reshape the data if we have more than one unit per pack
        if points_per_unit > 1:
            data.shape = (
                int(bin_data_points/points_per_unit), points_per_unit
            )

        return data

    def _mesh_data(self, directory, current_hash=None):
        """
        Return the mesh data (nodes, elements) for the dataset.

        """
        # parse nodes
        nodes_path = sorted(directory.glob('nodes.bin'))[0]
        nodes_hash = self._file_hash(nodes_path)
        nodes_format = binary_formats.nodes()

        # parse elements
        elements = {}
        elements_paths = sorted(directory.glob('elements.*.bin'))
        for elements_path in elements_paths:
            elements_type = re.search(
                r'elements\.(.*)\.bin', str(elements_path)).groups(0)[0]
            elements_hash = self._file_hash(elements_path)
            elements_format = getattr(binary_formats, elements_type)()

            elements[elements_type] = {}
            elements[elements_type]['path'] = elements_path
            elements[elements_type]['hash'] = elements_hash
            elements[elements_type]['fmt'] = elements_format

        # generate hash for all mesh files
        mesh_checksum = hashlib.sha1()
        mesh_checksum.update(nodes_hash.encode())
        for element in elements:
            mesh_checksum.update(elements[element]['hash'].encode())

        mesh_checksum = mesh_checksum.hexdigest()
        return_dict = {'hash': mesh_checksum}

        if current_hash is None or not (current_hash == mesh_checksum):
            return_dict['nodes'] = {}
            return_dict['nodes']['data'] = self._read_binary_data(
                nodes_path, nodes_format)
            return_dict['nodes']['fmt'] = nodes_format
            return_dict['elements'] = {}
            for element in elements:
                element_path = elements[element]['path']
                element_format = elements[element]['fmt']
                return_dict['elements'][element] = {}
                return_dict['elements'][element]['data'] = (
                    self._read_binary_data(element_path, element_format))
                return_dict['elements'][element]['fmt'] = (
                    element_format)

        else:
            return_dict['nodes'] = None
            return_dict['elements'] = None

        return return_dict

    def _field_data(self, directory, field, current_hash=None):
        """
        Return the field data for the dataset.

        """
        field_paths = sorted(directory.glob('**/*.bin'))

        for index, field_path in enumerate(field_paths):

            field_name = re.search(
                r'(.*)\.bin', str(field_path.name)).groups(0)[0]

            if field_name == field:
                directory = field_path.parent.name

                actual_field_path = field_path

                if directory == 'no':
                    field_format = binary_formats.nodal_fields()
                if directory == 'eo':
                    field_format = binary_formats.elemental_fields()

                field_hash = self._file_hash(field_path)

                break

        # this gets called if no break occured
        else:
            # field was not found
            return None

        if current_hash is None or not (current_hash == field_hash):
            data = self._read_binary_data(actual_field_path, field_format)
        else:
            data = None

        return {
            'hash': field_hash,
            'fmt': field_format,
            'field': data
        }

    def _blank_field(self):
        """
        Create an empty field.

        """
        ret_dict = {
            'hash': None,
            'fmt': binary_formats.nodal_fields(),
            'field': [0]*self._surface_node_count
        }
        return ret_dict

    def timestep_data(self, timestep, field, hash_dict=None):
        """
        Return the data for a given timestep and field and save it.

        Args:
         timestep (str): The timestep from which we want to get data.
         field (str): The field from which we want to get data.
         hash_dict (bool, optional, defaults to False): Read the data again,
          even if we already have data corresponding to the selected timestep
          and field.

        Returns:
         dict or None: The data for the timestep or None, if the field could
         not be found.

        Raises:
         TypeError: If ``type(timestep)`` is not `str`.
         TypeError: If ``type(field)`` is not `str`.
         TypeError: If ``type(hash_dict)`` is not `bool`.

        """
        return_dict =  {
            'nodes': None,
            'tets': None,
            'nodes_center': None,
            'field': None,
            'wireframe': None,
            'free_edges': None
        }

        if not isinstance(timestep, str):
            raise TypeError('timestep is {}, expected str'.format(
                type(timestep).__name__))

        if not isinstance(field, str):
            raise TypeError('field is {}, expected str'.format(
                type(field).__name__))

        if hash_dict is not None:
            if not isinstance(hash_dict, dict):
                raise TypeError('hash_dict is {}, expected dict'.format(
                    type(hash_dict).__name__))

        timestep_path = self.fo_dir / timestep

        try:
            mesh_dict = self._mesh_data(
                timestep_path, current_hash=hash_dict['mesh'])
            field_dict = self._field_data(
                timestep_path, field, current_hash=hash_dict['field'])

        except (TypeError, KeyError):
            mesh_dict = self._mesh_data(
                timestep_path, current_hash=None)
            field_dict = self._field_data(
                timestep_path, field, current_hash=None)

        mesh_nodes = mesh_dict['nodes']
        mesh_elements = mesh_dict['elements']

        # if we actually have to extract the surface again
        if mesh_nodes is not None:
            surface = dm.model_surface(mesh_nodes, mesh_elements)

            self.field_map = surface['field_map']

            return_dict['nodes'] = surface['nodes']
            self._surface_node_count = surface['node_count']
            return_dict['tets'] = surface['tets']
            return_dict['nodes_center'] = surface['nodes_center']
            return_dict['free_edges'] = surface['free_edges']
            return_dict['wireframe'] = surface['wireframe']

            self._surface_node_count = int(len(surface['tets']['data'])/3)

        # field does not exist
        if field_dict is None:
            field_values = self._blank_field()
        else:
            field_values = field_dict['field']

        return_dict['field'] = dm.model_surface_fields(
            self.field_map, field_values)

        # if field_dict is None:
        #     return_dict['field'] = 'does_not_exist'
        #     return return_dict

        # # if field == '__no_field__':
        # #     field_values = self._blank_field()
        # # else:
        # field_values = field_dict['field']
        # print('hey')

        # if field_values is not None:
        #     return_dict['field'] = dm.model_surface_fields(
        #         self.field_map, field_values)

        return return_dict
