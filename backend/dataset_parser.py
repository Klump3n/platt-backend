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

        # self._nodal_field_map = None
        self._nodal_field_map_dict = {}
        # self._blank_field_node_count = None
        self._blank_field_node_count_dict = {}

        self._surface_triangulation_dict = {}

        # self._elemental_field_map = None
        # self._elemental_field_map_combined = None
        # self._elemental_surface_node_count = None

        self._field_dict = None

        self._mesh_elements = None
        # self._mesh_elements_dict = {}

        # store the surface mesh for both elemental and nodal
        self._compressed_model_surface = None
        # self._compressed_model_surface_dict = {}

    def _file_hash(self, file_path, update=None):
        """
        Return a SHA1 hash for a file.

        Args:
         file_path (os.PathLike): Path to file we want to have a hash for.
         update (str): An existing hash we want to update.

        Returns:
         str: The hash of the file.

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

        if update is not None:
            add_to_checksum = str.encode(update)  # convert to bytes
            checksum.update(add_to_checksum)

        return checksum.hexdigest()

    def _string_hash(self, string, update=None):
        """
        Return a SHA1 hash for a string.

        Args:
         string (str): String we want to have a hash for.
         update (str): An existing hash we want to update.

        Returns:
         str: The hash of the inputs.

        """
        string_in_bytes = string.encode()

        checksum = hashlib.sha1(string_in_bytes)

        if update is not None:
            add_to_checksum = str.encode(update)  # convert to bytes
            checksum.update(add_to_checksum)

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

    def _geometry_data(self, directory, elementset, current_hash=None):
        """
        Get the geometry data for the dataset.

        """
        # parse nodes
        nodes_path = sorted(directory.glob('nodes.bin'))[0]
        nodes_hash = self._file_hash(nodes_path)
        nodes_format = binary_formats.nodes()

        # parse elements
        elements = {}
        elements_paths = sorted(directory.glob('elements.*.bin'))
        for elements_path in elements_paths:  # PARALLELIZE ME
            elements_type = re.search(
                r'elements\.(.*)\.bin', str(elements_path)).groups(0)[0]
            elements_hash = self._file_hash(elements_path)
            elements_format = getattr(binary_formats, elements_type)()

            elements[elements_type] = {}
            elements[elements_type]['path'] = elements_path
            elements[elements_type]['hash'] = elements_hash
            elements[elements_type]['fmt'] = elements_format

        # calculate hash
        mesh_checksum = nodes_hash  # init with nodes
        for element in elements:    # add every element
            mesh_checksum = self._string_hash(
                elements[element]['hash'],
                update=mesh_checksum
            )
        # update the mesh hash with the selected elementset
        for element_type in elementset:  # add every elementset
            elementset_path = elementset[element_type]
            mesh_checksum = self._file_hash(
                elementset_path,
                update=mesh_checksum
            )

        return_dict = {'hash': mesh_checksum}

        if current_hash is None or mesh_checksum not in current_hash:

            return_dict['nodes'] = {}
            return_dict['nodes']['data'] = self._read_binary_data(
                nodes_path, nodes_format)
            return_dict['nodes']['fmt'] = nodes_format

            return_dict['elements'] = {}
            for element in elements:  # PARALLELIZE ME
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

    def _elementset_data(self, elementset):
        """
        Parse the elementset binary data.

        """
        if elementset == {}:
            return None

        return_dict = {}
        for element_type in elementset:

            # get the elementset
            elementset_path = elementset[element_type]
            elementset_fmt = binary_formats.elementset()
            elementset_data = self._read_binary_data(elementset_path, elementset_fmt)

            return_dict[element_type] = elementset_data

        return return_dict

    def _field_data(self, directory, field, elementset, current_hash=None):
        """
        Return the field data for the dataset.

        current_hash should contain all the hashes of the fields that we have
        in memory. If the field we are about to parse has a hash that is
        already in current_hash, the parsing is skipped and lots of work (and
        time) is saved.

        Args:
         directory (pathlib.Path): Path to the eo/no directories.
         field (dict): Dictionary containing the requested field type and name.
         current_hash (str, optional): Hash of the currently selected field.

        Returns:
         dict: The field data for the dataset, if no parsing was required it
          contains 'None'.

        """
        req_field_type = field['type']
        req_field_name = field['name']

        if req_field_type == 'nodal':
            field_format = binary_formats.nodal_fields()
        elif req_field_type == 'elemental':
            field_format = binary_formats.elemental_fields()
        else:
            return None

        # get every binary path in the subfolders of directory
        sub_dir = field_format['data_dir']

        if req_field_type == 'nodal':

            bin_paths = sorted(directory.glob('{}/{}*.bin'.format(sub_dir, req_field_name)))

            if bin_paths != []:
                bin_path = bin_paths[0]
                field_hash = self._file_hash(bin_path)
            else:
                return None

            # update the field hash with the selected elementset
            for element_type in elementset:  # add every elementset
                elementset_path = elementset[element_type]
                field_hash = self._file_hash(
                    elementset_path,
                    update=field_hash
                )

            if current_hash is None or field_hash not in current_hash:
                data = {
                    'nodal': self._read_binary_data(bin_path, field_format)
                }
            else:
                data = {'nodal': None}

        if req_field_type == 'elemental':

            bin_paths = sorted(directory.glob('{}/{}.*.bin'.format(sub_dir, req_field_name)))

            elements_to_load = {}

            if bin_paths != []:

                field_hash = ''  # init

                for path in bin_paths:
                    element_type = re.search(r'{}\.(.*)\.bin'.format(req_field_name), str(path)).groups(0)[0]
                    elements_to_load[element_type] = path
                    field_hash = self._file_hash(path, update=field_hash)

            else:
                return None

            # update the field hash with the selected elementset
            for element_type in elementset:  # add every elementset
                elementset_path = elementset[element_type]
                field_hash = self._file_hash(
                    elementset_path,
                    update=field_hash
                )

            if current_hash is None or field_hash not in current_hash:
                data = {
                    'elemental': {}
                }
                for element_key in elements_to_load:
                    element_path = elements_to_load[element_key]
                    data['elemental'][element_key] = self._read_binary_data(element_path, field_format)
            else:
                data = {'elemental': None}

        return {
            'hash': field_hash,
            'fmt': field_format,
            'type': req_field_type,
            'data': data
        }

    def _blank_field(self, node_count):
        """
        Create an empty field.

        Returns:
         dict: Basically surface field values, where every value is 0.

        """
        ret_dict = {
            'hash': None,
            'fmt': binary_formats.nodal_fields(),
            'data': {'nodal': [0.0]*node_count}
        }
        return ret_dict

    def timestep_data(self, timestep, field, elementset, hash_dict=None):
        """
        Return the data for a given timestep and field and save it.

        Args:
         timestep (str): The timestep from which we want to get data.
         field (dict): The field from which we want to get data. Structure is
          {'type': TYPE (str), 'name': NAME (str)}.
         elementset (dict): The elementset we want to parse. Can be empty. If
          empty we just parse everything.
         hash_dict (bool, optional, defaults to False): Read the data again,
          even if we already have data corresponding to the selected timestep
          and field. Has fields 'mesh' and 'field'.

        Returns:
         dict or None: The data for the timestep or None, if the field could
         not be found.

        """
        return_dict = {
            'hash_dict': {
                'mesh': None,
                'field': None
            },
            'nodes': {'data': None},
            'tets': {'data': None},
            'nodes_center': None,
            'field': {'data': None},
            'wireframe': {'data': None},
            'free_edges': {'data': None}
        }

        timestep_path = self.fo_dir / timestep

        try:
            mesh_dict = self._geometry_data(
                timestep_path, elementset, current_hash=hash_dict['mesh'])

        except (TypeError, KeyError):
            mesh_dict = self._geometry_data(
                timestep_path, elementset, current_hash=None)

        if field is not None:
            try:
                field_dict = self._field_data(
                    timestep_path, field, elementset, current_hash=hash_dict['field'])

            except (TypeError, KeyError):
                field_dict = self._field_data(
                    timestep_path, field, elementset, current_hash=None)

        else:
            # Corner case for unsetting the fields once they were set
            field_dict = None

        # no field_dict means we are showing a blank field
        if field_dict is None:
            field_type = 'nodal'
        else:
            field_type = field_dict['type']

        return_dict['hash_dict']['mesh'] = mesh_dict['hash']

        mesh_nodes = mesh_dict['nodes']
        mesh_elements = mesh_dict['elements']

        if mesh_elements is not None:
            self._mesh_elements = mesh_elements

        if mesh_nodes is not None:

            elementset_data = self._elementset_data(elementset)

            self._compressed_model_surface = dm.model_surface(mesh_elements, mesh_nodes, elementset_data)

            self._nodal_field_map_dict[mesh_dict['hash']] = self._compressed_model_surface['nodal_field_map']
            self._blank_field_node_count_dict[mesh_dict['hash']] = self._compressed_model_surface['old_max_node_index']
            self._surface_triangulation_dict[mesh_dict['hash']] = self._compressed_model_surface['surface_triangulation']

            return_dict['nodes'] = self._compressed_model_surface['nodes']
            return_dict['nodes_center'] = self._compressed_model_surface['nodes_center']
            return_dict['tets'] = self._compressed_model_surface['triangles']
            return_dict['wireframe'] = self._compressed_model_surface['wireframe']
            return_dict['free_edges'] = self._compressed_model_surface['free_edges']

        # field does not exist
        if field_dict is None:

            node_count = self._blank_field_node_count_dict[mesh_dict['hash']]
            field_values = self._blank_field(node_count)['data']['nodal']

            # this is necessary so we parse a new field when we need it
            field_hash = None
            # update the mesh hash with the selected elementset
            for element_type in elementset:  # add every elementset
                elementset_path = elementset[element_type]
                field_hash = self._file_hash(
                    elementset_path,
                    update=field_hash
                )
            return_dict['hash_dict']['field'] = field_hash

        else:

            if field_type == 'nodal':
                field_values = field_dict['data']['nodal']

            if field_type == 'elemental':

                elemental_field_dict = field_dict['data']['elemental']
                field_values = dm.expand_elemental_fields(elemental_field_dict, self._mesh_elements, self._surface_triangulation_dict[mesh_dict['hash']])

            return_dict['hash_dict']['field'] = field_dict['hash']

        if field_values is not None:

            if field_type == 'nodal':
                return_dict['field'] = dm.model_surface_fields_nodal(
                    self._nodal_field_map_dict[mesh_dict['hash']], field_values)

            if field_type == 'elemental':
                return_dict['field'] = dm.model_surface_fields_elemental(field_values)

        return return_dict
