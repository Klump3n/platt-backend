#!/usr/bin/env python3
"""
Access and store data for a dataset.

"""
import os
import numpy as np
import struct


class LoadData:
    """
    Load the data from a dataset.

    """
    def __init__(self, dataset_path):
        """
        Initialize the data with an initial timestep.

        """
        self.dataset_path = dataset_path

        self.surface_data = {}

    def wireframe(self, timestep):
        """
        Extract the wireframe for a given timestep.

        """
        pass

    def _get_binary_data(self, binary_file, binary_format):
        """
        Unpack a binary file according to the spec given in binary_format.

        binary_format is a dict, containing
         data_point_size (int): The number of bytes per data point
         data_point_type (str): The data type (d = double, i = integer)
         points_per_unit (int): The number of data points that belong together.

        Args:
         binary_file (os.PathLike): The path to the binary file.
         binary_format (dict): A dictionary containing the number of bytes per
          data point, the format of the data point (int, double, ...) and the
          number of data points that make up a unit (see above).

        Returns:
         None or np.array: None of the binary_file does not exist, else a
         np.array with the binary data.

        Raises:
         TypeError: If ``type(binary_file)`` is not `os.PathLike`.
         TypeError: If ``type(binary_format)`` is not `dict`.

        """
        if not isinstance(binary_file, os.PathLike):
            raise TypeError(
                'binary_file is {}, expected os.PathLike'.format(
                    type(binary_file).__name__))

        if not isinstance(binary_format, dict):
            raise TypeError(
                'binary_format is {}, expected dict'.format(
                    type(binary_format).__name__))

        if not binary_file.exists():
            return None

        # let this just raise a KeyError if we hand it a wrong dict
        data_point_size = binary_format['data_point_size']
        data_point_type = binary_format['data_point_type']
        points_per_unit = binary_format['points_per_unit']

        open_binary_file = open(binary_file, 'rb')  # read, binary
        bin_data = open_binary_file.read()
        bin_data_points = int(len(bin_data) / data_point_size)

        # little endian
        struct_format = '<{}{}'.format(bin_data_points, data_point_type)

        data = struct.unpack(struct_format, bin_data)

        # reshape the data
        data = np.asarray(data)
        data.shape = (int(bin_data_points/points_per_unit), points_per_unit)

        return data

