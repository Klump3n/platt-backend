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

import cherrypy

from util.loggers import BackendLog as bl

class ParseDataset:
    """
    Unpack and store data for a dataset.

    """
    def __init__(self, source_dict=None, dataset_name=None):
        """
        Initialize the parser.

        Args:
         dataset_dir (os.PathLike): The dataset directory that contains all
          the information about the dataset.

        Raises:
         TypeError: If ``type(dataset_dir)`` is not `os.PathLike`.

        """
        self.source = source_dict
        self.source_type = source_dict['source']

        self._dataset_name = dataset_name

        if self.source_type == 'local':
            data_dir = self.source['local']

            # Check if the path exists
            if not data_dir.exists():
                raise ValueError(
                    '{} does not exist'.format(data_dir.absolute()))

            # Set the data dir
            self._data_dir = data_dir.absolute()

            self.dataset_dir = self._data_dir / dataset_name
            self.fo_dir = self.dataset_dir / 'fo'

            # Check if the path exists
            if not self.dataset_dir.exists():
                raise ValueError(
                    '{} does not exist'.format(self.dataset_dir.absolute()))

        if self.source_type == 'external':
            self.ext_addr = source_dict['external']['addr']
            self.ext_port = source_dict['external']['port']

        # self._nodal_field_map = None
        self._nodal_field_map_dict = {}
        # self._blank_field_node_count = None
        self._blank_field_node_count_dict = {}

        self._surface_triangulation_dict = {}

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

    def _binary_hash(self, binary_blob, update=None):
        """
        Return the sha1 sum for a binary blob.

        Args:
         binary_blob (binary): Binary blob we want to hash.
         update (str): An existing hash we want to update.

        Returns:
         str: The hash of the file.

        """
        checksum = hashlib.sha1()
        objhash = hashlib.sha1(binary_blob).hexdigest()
        checksum.update(objhash)

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

    def _read_binary_data_external(self, object_key_list, fmt_list):
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

        # import sys

        # def get_size(obj, seen=None):
        #     """Recursively finds size of objects"""
        #     size = sys.getsizeof(obj)
        #     if seen is None:
        #         seen = set()
        #     obj_id = id(obj)
        #     if obj_id in seen:
        #         return 0
        #     # Important mark as seen *before* entering recursion to gracefully handle
        #     # self-referential objects
        #     seen.add(obj_id)
        #     if isinstance(obj, dict):
        #         size += sum([get_size(v, seen) for v in obj.values()])
        #         size += sum([get_size(k, seen) for k in obj.keys()])
        #     elif hasattr(obj, '__dict__'):
        #         size += get_size(obj.__dict__, seen)
        #     elif hasattr(obj, '__iter__') and not isinstance(obj, (str, bytes, bytearray)):
        #         size += sum([get_size(i, seen) for i in obj])
        #     return size


        if len(object_key_list) != len(fmt_list):
            return None
        return_list = []
        # print(fmt_list)
        import backend.interface_external_data as ext_data

        print(object_key_list)
        # bin_data = [{object: X, namespace: X, contents: X, sha1sum: X}, ...]
        bin_data = ext_data.simulation_file(
            source_dict=self.source,
            namespace=self._dataset_name,
            object_key_list=object_key_list
        )
        # print(len(bin_data))
        # import sys
        # print(get_size(bin_data))

        # for d in bin_data:
        #     print(get_size(d))

        # sys.exit()
        for it, fmt in enumerate(fmt_list):

            bin_data_entry = bin_data[it]
            bin_data_entry_contents = bin_data_entry["contents"]

            # let this just raise a KeyError if we hand it a wrong dict
            data_point_size = fmt['data_point_size']
            data_point_type = fmt['data_point_type']
            points_per_unit = fmt['points_per_unit']

            bin_data_points = int(len(bin_data_entry_contents) / data_point_size)

            # little endian
            struct_format = '<{}{}'.format(bin_data_points, data_point_type)

            data = struct.unpack(struct_format, bin_data_entry_contents)
            data = np.asarray(data)

            # reshape the data if we have more than one unit per pack
            if points_per_unit > 1:
                data.shape = (
                    int(bin_data_points/points_per_unit), points_per_unit
                )

            r_dict = dict()
            r_dict["namespace"] = bin_data_entry["namespace"]
            r_dict["object"] = bin_data_entry["object"]
            r_dict["contents"] = data
            r_dict["sha1sum"] = bin_data_entry["tags"]["sha1sum"]

            if r_dict["sha1sum"] == "":
                bl.verbose_warning("No sha1sum from proxy")

            return_list.append(r_dict)

        return return_list

    def _geometry_data(self, timestep, elementset, current_hash=None):
        """
        Get the geometry data for the dataset.

        TODO: Refactor this stuff

        """
        if self.source_type == 'local':
            return self._geometry_data_local(timestep, elementset, current_hash)
        if self.source_type == 'external':
            return self._geometry_data_external(timestep, elementset, current_hash)
        else:
            return None

    def _geometry_data_local(self, timestep, elementset, current_hash=None):

        directory = self.fo_dir / timestep

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

    def _geometry_data_external(self, timestep, elementset, current_hash=list()):
        """
        Get data from the gateway.

        Procedure is as follows:
         * try to calculate the hash from the index (in fixed order)
          * if this fails (e.g. a single hash is missing) we download every file
            from the gateway
          * if this succeeds and the hash is identical to current_hash return
            None -> no action necessary
          * if this succeeds and the hash is NOT identical to current_hash we
            download every file from the gateway
         * we downloaded all files -> calculate the hash (in fixed order)
          * if the hash is identical to current_hash return None -> no action
            necessary
          * if the hash is NOT identical to current_hash return downloaded data

        Fixed order for hash calculation is (if existent)
        * nodes
        * elements (sorted by dictionary)
        * skins (sorted by dictionary)

        We don't download elementsets here.

        """
        return_dict = dict()

        # This is so dumb.
        import backend.global_settings as gloset
        ext_index = gloset.scene_manager.ext_src_dataset_index(
            update=False, dataset=self._dataset_name)
        timestep_dict = ext_index[self._dataset_name][timestep]

        print(timestep_dict)
        # parse nodes
        nodes_key = timestep_dict['nodes']['object_key']
        nodes_hash = timestep_dict['nodes']['sha1sum']
        nodes_format = binary_formats.nodes()

        # parse elements
        elements = {}
        elements_types = list(timestep_dict['elements'].keys())
        for elements_type in elements_types:
            if elements_type in binary_formats.valid_element_types():

                current_elem = timestep_dict['elements']

                elements_format = getattr(binary_formats, elements_type)()

                elements[elements_type] = {}
                elements[elements_type]['key'] = current_elem[elements_type]['object_key']
                elements[elements_type]['hash'] = current_elem[elements_type]['sha1sum']
                elements[elements_type]['fmt'] = elements_format

        skins = {}
        try:
            skin_element_types = list(timestep_dict["skin"].keys())
            current_skin = timestep_dict['skin']
            skin_format = binary_formats.skin()

            for element_type in skin_element_types:
                if element_type in binary_formats.valid_element_types():
                    skins[element_type] = {}
                    skins[element_type]['key'] = current_skin[element_type]['object_key']
                    skins[element_type]['hash'] = current_skin[element_type]['sha1sum']
                    skins[element_type]['fmt'] = skin_format

        except KeyError as e:
            bl.debug_warning("No skins found: {}".format(e))

        # calculate the hash if we have the sha1sums in the index, else just
        # get everything for every timestep
        hash_list = list()
        hash_list.append(nodes_hash)
        for element in elements:
            hash_list.append(elements[element]['hash'])
        # for element_type in elementset:
        #     hash_list.append(elementset[element_type]['sha1sum'])
        for skin in skins:
            hash_list.append(skins[element_type]['hash'])

        calc_hashes = True
        for one_hash in hash_list:
            if one_hash == "":
                calc_hashes = False

        # init to None
        mesh_checksum = None

        if calc_hashes:

            for one_hash in hash_list:
                mesh_checksum = self._string_hash(
                    one_hash,
                    update=mesh_checksum
                )

        if (
                current_hash is list() or
                mesh_checksum is None or
                mesh_checksum not in current_hash
        ):

            # reset mesh checksum
            mesh_checksum = None

            object_key_list = []
            fmt_list = []

            object_key_list.append(nodes_key)
            fmt_list.append(nodes_format)

            for element in elements:
                object_key_list.append(elements[element]['key'])
                fmt_list.append(elements[element]['fmt'])
            for skin in skins:
                object_key_list.append(skins[skin]['key'])
                fmt_list.append(skins[skin]['fmt'])

            geom_dict_data = self._read_binary_data_external(object_key_list, fmt_list)

            geom_data = list()
            for d in geom_dict_data:
                geom_data.append(d["contents"])
                mesh_checksum = self._string_hash(
                    d["sha1sum"],
                    update=mesh_checksum
                )

            if mesh_checksum in current_hash:
                return_dict['hash'] = mesh_checksum
                return_dict['nodes'] = None
                return_dict['elements'] = None
                return_dict['skins'] = None
                return return_dict

            return_dict['hash'] = mesh_checksum
            return_dict['nodes'] = {}
            return_dict['nodes']['fmt'] = nodes_format
            return_dict['nodes']['data'] = geom_data[0]

            return_dict['elements'] = {}
            for it, element in enumerate(elements):
                element_path = elements[element]['key']

                return_dict['elements'][element] = {}
                return_dict['elements'][element]['fmt'] = elements[element]['fmt']
                return_dict['elements'][element]['data'] = geom_data[it+1]

            return_dict["skins"] = {}
            for it, skin in enumerate(skins):
                skin_path = skins[skin]['key']

                return_dict["skins"][skin] = {}
                return_dict["skins"][skin]['fmt'] = skins[skin]['fmt']
                return_dict["skins"][skin]['data'] = geom_data[it+1+len(elements)]

        else:
            return_dict['hash'] = mesh_checksum
            return_dict['nodes'] = None
            return_dict['elements'] = None
            return_dict['skins'] = None

        return return_dict

    def _elementset_data(self, elementset):
        """
        Parse the elementset binary data.

        """
        if self.source_type == 'local':
            return self._elementset_data_local(elementset)
        if self.source_type == 'external':
            return self._elementset_data_external(elementset)
        else:
            return None

    def _elementset_data_local(self, elementset):
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

    def _elementset_data_external(self, elementset):
        # # This is so dumb.
        # import backend.global_settings as gloset
        # ext_index = gloset.scene_manager.ext_src_index()
        # elset_dict = ext_index[self._dataset_name][timestep]['elset']

        if elementset == {}:
            return None

        return_dict = {}

        elset_key_list = []
        elset_fmt_list = []

        elementset_fmt = binary_formats.elementset()

        for element_type in elementset:
            elset_key_list.append(elementset[element_type]['object_key'])
            elset_fmt_list.append(elementset_fmt)

        elementset_dict_data = self._read_binary_data_external(elset_key_list, elset_fmt_list)

        for it, element_type in enumerate(elementset):
            return_dict[element_type] = elementset_dict_data[it]["contents"]

        return return_dict


    def _field_data(self, timestep, field, elementset, current_hash=None):
        """
        Return the field data for the dataset.

        current_hash should contain all the hashes of the fields that we have
        in memory. If the field we are about to parse has a hash that is
        already in current_hash, the parsing is skipped and lots of work (and
        time) is saved.

        Args:
         timestep (str): Requested timestep.
         field (dict): Dictionary containing the requested field type and name.
         current_hash (str, optional): Hash of the currently selected field.

        Returns:
         dict: The field data for the dataset, if no parsing was required it
          contains 'None'.

        """
        if self.source_type == 'local':
            return self._field_data_local(timestep, field, elementset, current_hash=None)
        if self.source_type == 'external':
            return self._field_data_external(timestep, field, elementset, current_hash=None)
        else:
            return None

    def _field_data_local(self, timestep, field, elementset, current_hash=None):
        directory = self.fo_dir / timestep

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

    def _field_data_external(self, timestep, field, elementset, current_hash=None):

        # This is so dumb.
        import backend.global_settings as gloset
        ext_index = gloset.scene_manager.ext_src_dataset_index(
            update=False, dataset=self._dataset_name)
        timestep_dict = ext_index[self._dataset_name][timestep]

        req_field_type = field['type']
        req_field_name = field['name']

        if req_field_type == 'nodal':
            field_format = binary_formats.nodal_fields()
        elif req_field_type == 'elemental':
            field_format = binary_formats.elemental_fields()
        else:
            return None

        field_hash = None

        if req_field_type == 'nodal':

            hash_list = list()

            hash_list.append(timestep_dict['nodal'][req_field_name]['sha1sum'])
            for element_type in elementset:
                hash_list.append(elementset[element_type]['sha1sum'])

            calc_hashes = True
            for one_hash in hash_list:
                if one_hash == "":
                    calc_hashes = False

            if calc_hashes:
                for one_hash in hash_list:
                    field_hash = self._string_hash(
                        one_hash,
                        update=field_hash
                    )

            object_key = timestep_dict['nodal'][req_field_name]['object_key']

            if current_hash is None or field_hash is None or field_hash not in current_hash:
                nodal_field_data = self._read_binary_data_external([object_key], [field_format])[0]  # get the only thing in the array
                field_hash = nodal_field_data["sha1sum"]
                data = {
                    'nodal': nodal_field_data["contents"]
                }
            else:
                data = {'nodal': None}

        if req_field_type == 'elemental':

            elem_types = list(timestep_dict['elemental'][req_field_name].keys())
            elements_to_load = {}

            hash_list = list()

            for elem_type in elem_types:
                hash_list.append(timestep_dict['elemental'][req_field_name][elem_type]['sha1sum'])
            for element_type in elementset:
                hash_list.append(elementset[element_type]['sha1sum'])

            calc_hashes = True
            for one_hash in hash_list:
                if one_hash == "":
                    calc_hashes = False

            if calc_hashes:
                for one_hash in hash_list:
                    field_hash = self._string_hash(
                        one_hash,
                        update=field_hash
                    )

                # update the field hash with the selected elementset
                for element_type in elementset:
                    elementset_sha1 = elementset[element_type]['sha1sum']
                    field_hash = self._string_hash(
                        elementset_sha1,
                        update=field_hash
                    )

            for elem_type in elem_types:

                object_key = timestep_dict['elemental'][req_field_name][elem_type]['object_key']
                object_hash = timestep_dict['elemental'][req_field_name][elem_type]['sha1sum']

                elements_to_load[elem_type] = object_key

            if current_hash is None or field_hash is None or field_hash not in current_hash:
                data = {
                    'elemental': {}
                }

                elements_to_load_list = []
                fmt_list = []
                for element_key in elements_to_load:
                    elements_to_load_list.append(elements_to_load[element_key])
                    fmt_list.append(field_format)

                element_data_dict_list = self._read_binary_data_external(elements_to_load_list, fmt_list)
                element_data_list = list()
                for d in element_data_dict_list:
                    element_data_list.append(d["contents"])

                for it, element_key in enumerate(elements_to_load):
                    data['elemental'][element_key] = element_data_list[it]


                for one_field in element_data_dict_list:
                    one_hash = one_field["sha1sum"]
                    field_hash = self._string_hash(
                        one_hash,
                        update=field_hash
                    )

                # update the field hash with the selected elementset
                for element_type in elementset:
                    elementset_sha1 = elementset[element_type]['sha1sum']
                    field_hash = self._string_hash(
                        elementset_sha1,
                        update=field_hash
                    )

            else:
                data = {'elemental': None}

        return_dict = {
            'hash': field_hash,
            'fmt': field_format,
            'type': req_field_type,
            'data': data
        }
        return return_dict


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

        try:
            mesh_dict = self._geometry_data(
                timestep, elementset, current_hash=hash_dict['mesh'])

        except (TypeError, KeyError) as e:
            bl.debug_warning("No mesh for given hash_dict found: {}".format(e))
            mesh_dict = self._geometry_data(
                timestep, elementset, current_hash=None)
            raise

        if field is not None:
            try:
                field_dict = self._field_data(
                    timestep, field, elementset, current_hash=hash_dict['field'])

            except (TypeError, KeyError) as e:
                bl.debug_warning("No field for given hash_dict found: {}".format(e))
                field_dict = self._field_data(
                    timestep, field, elementset, current_hash=None)

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
        mesh_skins = mesh_dict["skins"]

        if mesh_elements is not None:
            self._mesh_elements = mesh_elements

        if mesh_nodes is not None:

            elementset_data = self._elementset_data(elementset)

            self._compressed_model_surface = dm.model_surface(mesh_elements, mesh_nodes, mesh_skins, elementset_data)

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
            field_hash = self._string_hash(
                str(node_count),
                update=field_hash
            )

            # update the mesh hash with the selected elementset
            if self.source_type == 'local':
                for element_type in elementset:  # add every elementset
                    elementset_path = elementset[element_type]
                    field_hash = self._file_hash(
                        elementset_path,
                        update=field_hash
                    )
            if self.source_type == 'external':
                for element_type in elementset:  # add every elementset
                    elementset_sha1 = elementset[element_type]['sha1sum']
                    field_hash = self._string_hash(
                        elementset_sha1,
                        update=field_hash
                    )
            return_dict['hash_dict']['field'] = field_hash

        # field dict is not None
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
