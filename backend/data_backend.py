#!/usr/bin/env python3
"""
Unpack some binary files and finds the surface of the mesh. Right now this is
limited to C3D8 file format.

"""
import struct
import numpy as np
import matplotlib.cm as cm
# import sys


class UnpackMesh:
    """
    Unpack mesh data from two binary files and do some magic to it.

    """
    def __init__(self, node_path, element_path):
        """
        Initialise the mesh unpacking class by:

        - unpacking the nodes and the elements of the mesh
        - initialising the timestep array
        - initialising the surface quads for the elements
        - initialising the triangulated surface

        Args:
         node_path (str): The path to the data.

        """
        self.get_binary_data(node_path, do='unpack', what='nodes')
        self.get_binary_data(element_path, do='unpack', what='elements')
        self.timesteps = []
        self.surface_quads = None
        self.surface_triangles = None
        self.unique_surface_triangles = None

    def add_timestep(self, path):
        """
        Wrapper around the get_binary_data function.

        This just calls the function with pre-selected arguments, makes adding
        a timestep less confusing.

        Args:
         path (str): 
        """
        return self.get_binary_data(path, do='add', what='timestep')

    def get_binary_data(
            self, path,
            do,                 # {'unpack', 'add'}
            what                # {'nodes', 'elements', 'timestep'}
    ):
        """Unpack binary data.

        Specifying the what to do will either unpack nodes or elements or
        add a timestep to self.timesteps.

        Open a file and read it as binary, unpack into an array in a specified
        format, cast the array to numpy and reshape it.
        """
        if (do == 'unpack' and what == 'nodes'):
            size_of_data = 8    # 8 bytes of ...
            data_type = 'd'     # ... doubles
            points_per_unit = 3  # 3 coords per node
        elif (do == 'unpack' and what == 'elements'):
            size_of_data = 4    # 4 bytes of ...
            data_type = 'i'     # ... integers
            points_per_unit = 8  # 8 points per element
        elif (do == 'add' and what == 'timestep'):
            size_of_data = 8    # 8 bytes of ...
            data_type = 'd'     # ... doubles
            points_per_unit = 1  # 1 data point per unit.
        else:
            raise ValueError('Unknown parameters. Doing nothing.')

        f = open(path, 'rb')
        bin_data = f.read()
        bin_data_points = int(len(bin_data) / size_of_data)

        # I.e. '<123i' or '<123d' for bin_data_points = 123
        struct_format = '<{size}'.format(size=bin_data_points) + data_type

        data = struct.unpack(struct_format, bin_data)
        data = np.asarray(data)
        data.shape = (int(bin_data_points/points_per_unit), points_per_unit)
        if (do == 'unpack' and what == 'nodes'):
            self.nodes = data
            print('Parsed {nodes_t} nodes.'.format(
                nodes_t=data.shape[0]))
        elif (do == 'unpack' and what == 'elements'):
            self.elements = data
            print('Parsed {elements_t} elements.'.format(
                elements_t=data.shape[0]))
        elif (do == 'add', what == 'timestep'):
            data = np.asarray(data)
            self.timesteps.append(data)
        return data

    def generate_surfaces_for_elements(self):
        """
        Finds the outward faces of the mesh (in other words: the surface).
        Returns a numpy array with the surface faces.

        The mesh consists of cubic elements with corner nodes.
        Count the unique occurrences of each node. For each element generate
        the six (outward pointing) faces. Iterate over all the points of
        each face and add the occurrences (as previously generated) up.
        Faces at the corner will have a count of 9, faces at the border a
        count of 12 and faces in the middle of the plane a count of 16.
        (You might want to draw it on a piece of paper.)

        """
        # self.elements is a map that points from each element to the nodes
        # that constitute an element. In that sense two neighbouring elements
        # will share at least 1 (corner) node. So that node will then appear
        # at least twice in self.elements
        _, node_counts = np.unique(self.elements,
                                   return_counts=True)

        # The ordering of the element indices that generate six outward
        # pointing faces. Each element has 8 entries, counting from 0.
        element_faces = [
            [0, 1, 5, 4],
            [1, 2, 6, 5],
            [2, 3, 7, 6],
            [3, 0, 4, 7],
            [4, 5, 6, 7],
            [3, 2, 1, 0]
        ]

        surfaces = []

        # FIXME: Can this function be deleted?
        # def append_face_to_surfaces(element, element_face):
        #     """Append the face to the output array.
        #     """
        #     face = [
        #         element[element_face[0]],
        #         element[element_face[1]],
        #         element[element_face[2]],
        #         element[element_face[3]]
        #     ]
        #     surfaces.append(face)

        for element in self.elements:
            for element_face in element_faces:
                node_weight = node_counts[element[element_face[0]]] \
                              + node_counts[element[element_face[1]]] \
                              + node_counts[element[element_face[2]]] \
                              + node_counts[element[element_face[3]]]

                if (
                        (node_weight == 9) or  # Corner faces
                        (node_weight == 12) or  # Border faces
                        (node_weight == 16)     # Plane faces
                ):
                    face = [
                        element[element_face[0]],
                        element[element_face[1]],
                        element[element_face[2]],
                        element[element_face[3]]
                    ]
                    surfaces.append(face)

                    # FIXME: Can this function call be deleted?
                    # append_face_to_surfaces(element, element_face)

                else:
                    pass

        self.surface_quads = np.asarray(surfaces)
        print('Parsed {surface_quads_t} surface quads.'.format(
            surface_quads_t=self.surface_quads.shape[0]))
        return self.surface_quads

    def generate_triangles_from_quads(self):
        """From our list of quads generate outward pointing triangles.
        """
        if (self.surface_quads is None):
            self.generate_surfaces_for_elements()

        triangles = []

        # Two triangles in every quad. This generates outward pointing
        # triangles.
        polygon_coordinates_in_quad = [
            [0, 1, 2],
            [0, 2, 3]
        ]

        print('Triangulating surface.')

        for quad in self.surface_quads:
            for polygon_coord in polygon_coordinates_in_quad:
                triangle = [
                    quad[polygon_coord[0]],
                    quad[polygon_coord[1]],
                    quad[polygon_coord[2]],
                ]
                triangles.append(triangle)

        self.surface_triangles = np.asarray(triangles)
        print('Parsed {surface_triangles_t} surface triangles.'.format(
            surface_triangles_t=self.surface_triangles.shape[0]))
        return self.surface_triangles

    def return_unique_surface_nodes(self):
        """Returns the unique surface triangles.
        """
        if (self.unique_surface_triangles is None):
            self.generate_unique_surface_triangles()

        unique_surface_nodes = []
        for triangle in self.unique_surface_triangles:
            for corner in [0, 1, 2]:
                unique_surface_nodes.append(self.nodes[triangle][corner])

        return unique_surface_nodes

    def return_surface_indices(self):
        """Returns the indices for the OpenGL array triangles.

        If a node is already present by means of another triangle, we dont want
        to output it too. We dont want redundancy.
        """
        if (self.unique_surface_triangles is None):
            self.generate_unique_surface_triangles()

        # Figure out how many unique nodes we have.
        unique_nodes = np.unique(self.elements).shape[0]

        # Initialise an array for those unique nodes with None for every
        # element.
        self.node_map = [None]*unique_nodes

        # Overwrite the None in this array with an index for the unique
        # elements.
        for index, value in enumerate(self.unique_surface_triangles):
            self.node_map[value] = index

        # We want to find out which index belongs to every corner of every
        # triangle.
        index_list = []
        for triangle in self.surface_triangles:
            for corner in triangle:
                index_list.append(self.node_map[corner])

        return index_list

    def HACK_return_data_for_unique_nodes(self, path):
        """
        Hacked this thing real quick.

        """
        if (self.unique_surface_triangles is None):
            self.generate_unique_surface_triangles()

        timestep_data = self.add_timestep(path)

        timestep_data = timestep_data.flatten().tolist()

        unique_surface_data = []
        for triangle in self.unique_surface_triangles:
            unique_surface_data.append(timestep_data[triangle])

        print(min(unique_surface_data), max(unique_surface_data))
        return unique_surface_data

    def return_data_for_unique_nodes(self, object_name, field, timestep):
        """Returns the (i.e.) temperature data for unique nodes.
        """
        if (self.unique_surface_triangles is None):
            self.generate_unique_surface_triangles()

        # NOTE: Fixme.
        timestep_data = self.add_timestep(object_name+'/fo/'+timestep+'/no/'+field+'.bin')

        unique_surface_data = []
        for triangle in self.unique_surface_triangles:
            unique_surface_data.append(timestep_data[triangle])

        return unique_surface_data

    def generate_unique_surface_triangles(self):
        """Generate the unique surface triangles from all the surface_triangles.
        """
        if (self.surface_triangles is None):
            self.generate_triangles_from_quads()

        self.unique_surface_triangles = np.unique(self.surface_triangles)

    def generate_temperature_file(self, timestep):

        def get_rgb(temp):
            # NOTE: this takes considerable time. Use binning later on.
            # Or even give everything to the shader.
            # Good ones are afmhot, CMRmap, gist_heat, gnuplot, gnuplot2.
            # See http://matplotlib.org/users/colormaps.html for more.
            color = cm.gnuplot2(int(temp), bytes=True)
            return '{r},{g},{b}'.format(r=color[0], g=color[1], b=color[2])

        unique_triangles = np.unique(self.surface_triangles)

        print('Writing temperatures for timestep {timestep_t}'.format(
            timestep_t=timestep))
        temperature_file = open('welding_sim.temperatures', 'w')

        # Split up because the last one can not have a newline or comma.
        for triangle in unique_triangles[:-1]:
            temp_string = get_rgb(float(self.timesteps[timestep][triangle]))
            temperature_file.write(temp_string + ',')
        for triangle in unique_triangles[-1:]:
            temp_string = get_rgb(float(self.timesteps[timestep][triangle]))
            temperature_file.write(temp_string)

        temperature_file.close()

    def return_metadata(self):
        """Get the meta-data for the mesh.

        Size, etc.
        """
        if (self.surface_triangles is None):
            self.generate_triangles_from_quads()

        x_nodes = []
        y_nodes = []
        z_nodes = []
        unique_triangles = np.unique(self.surface_triangles)
        for node in unique_triangles:
            x_nodes.append(self.nodes[node][0])
            y_nodes.append(self.nodes[node][1])
            z_nodes.append(self.nodes[node][2])
        x_nodes = np.asarray(x_nodes)
        y_nodes = np.asarray(y_nodes)
        z_nodes = np.asarray(z_nodes)
        x_min = x_nodes.min()
        x_max = x_nodes.max()
        y_min = y_nodes.min()
        y_max = y_nodes.max()
        z_min = z_nodes.min()
        z_max = z_nodes.max()
        x_center = (x_max + x_min)/2
        y_center = (y_max + y_min)/2
        z_center = (z_max + z_min)/2

        # metafile = open('welding_sim.metafile', 'w')
        # metafile.write('{x_center_t},{y_center_t},{z_center_t}'.format(
        #     x_center_t=x_center, y_center_t=y_center, z_center_t=z_center))
        # metafile.close()
        return np.asarray([x_center, y_center, z_center])


if __name__ == '__main__':
    """If we use the file as a standalone program this is called.
    """

    # Some test case
    testdata = UnpackMesh(
        node_path='../example_data/object_a/fo/00.1/nodes.bin',
        element_path='../example_data/object_a/fo/00.1/elements.dc3d8.bin'
    )

    # Add a timestep
    # testdata.add_timestep('testdata/nt11@16.7.bin')
    # testdata.generate_triangle_files()
    # testdata.generate_temperature_file(timestep=0)
    # testdata.return_metadata()
    # testdata.return_surface()
    a = testdata.return_unique_surface_nodes()
    b = testdata.return_surface_indices()
    c = testdata.add_timestep('../example_data/object_a/fo/00.1/no/nt11.bin')
    d = testdata.HACK_return_data_for_unique_nodes('../example_data/object_a/fo/00.1/no/nt11.bin')
    print(len(a))
    print(len(b))
    print(len(c))
    print(len(d))
