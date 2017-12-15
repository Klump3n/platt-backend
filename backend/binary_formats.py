#!/usr/bin/env python3
"""
Element types for the fo format.

"""


def nodes():
    """
    The node binary format.

    """
    nodes_dict = {}

    file_name = 'nodes.bin'

    data_point_size = 8    # 8 bytes of ...
    data_point_type = 'd'     # ... doubles
    points_per_unit = 3  # 3 coords per node

    nodes_dict['file_name'] = file_name
    nodes_dict['data_point_size'] = data_point_size
    nodes_dict['data_point_type'] = data_point_type
    nodes_dict['points_per_unit'] = points_per_unit

    return nodes_dict


def nodal_fields():
    """
    The binary format for nodal fields.

    """

    nodal_field_dict = {}

    nodal_dir = 'no'

    data_point_size = 8    # 8 bytes of ...
    data_point_type = 'd'     # ... doubles
    points_per_unit = 1  # 1 data point per unit.

    nodal_field_dict['nodal_dir'] = nodal_dir
    nodal_field_dict['data_point_size'] = data_point_size
    nodal_field_dict['data_point_type'] = data_point_type
    nodal_field_dict['points_per_unit'] = points_per_unit

    return nodal_field_dict


def c3d8():
    """
    The c3d8 binary format.

    We parse 4 bytes of integers that are grouped into packs of 8, because an
    element in this format consists of 8 nodes.

    """
    c3d8_dict = {}

    file_name = 'elements.c3d8.bin'

    data_point_size = 4    # 4 bytes of ...
    data_point_type = 'i'     # ... integers
    points_per_unit = 8  # 8 points per element

    # For each element these are the indices in a pack of 8 nodes, that make
    # up the faces.
    faces = [
        [0, 3, 2, 1],
        [4, 5, 6, 7],
        [0, 1, 5, 4],
        [1, 2, 6, 5],
        [2, 3, 7, 6],
        [0, 4, 7, 3]
    ]

    # If we want to display the surface with WebGL we have to triangulate it.
    # Those indices make up a set of triangles with outward facing normal
    # vectors.
    quad_triangles = [
        [0, 1, 2],
        [0, 2, 3]
    ]

    face_triangles = []

    for face in faces:
        for triangle in quad_triangles:
            face_triangle = []
            for corner in triangle:
                face_triangle.append(face[corner])
            face_triangles.append(face_triangle)

    # For each element these are the indices in a pack of 8 nodes, that make
    # up the edges.
    edges = [
        [0, 1],
        [1, 2],
        [2, 3],
        [3, 0],
        [4, 5],
        [5, 6],
        [6, 7],
        [7, 4],
        [0, 4],
        [1, 5],
        [2, 6],
        [3, 7]
    ]

    c3d8_dict['file_name'] = file_name
    c3d8_dict['data_point_size'] = data_point_size
    c3d8_dict['data_point_type'] = data_point_type
    c3d8_dict['points_per_unit'] = points_per_unit

    c3d8_dict['faces'] = faces
    c3d8_dict['face_triangles'] = face_triangles
    c3d8_dict['edges'] = edges

    return c3d8_dict


def c3d6():
    """
    The c3d6 binary format.

    We parse 4 bytes of integers that are grouped into packs of 6, because an
    element in this format consists of 6 nodes.

    """
    c3d6_dict = {}

    file_name = 'elements.c3d6.bin'

    data_point_size = 4    # 4 bytes of ...
    data_point_type = 'i'     # ... integers
    points_per_unit = 6  # 8 points per element

    # For each element these are the indices in a pack of 6 nodes, that make
    # up the faces.
    faces = [
        [0, 2, 1],
        [3, 4, 5],
        [0, 1, 4, 3],
        [1, 2, 5, 4],
        [2, 0, 3, 5]
    ]

    # If we want to display the surface with WebGL we have to triangulate it.
    # Those indices make up a set of triangles with outward facing normal
    # vectors.
    quad_triangles = [
        [0, 1, 2],
        [0, 2, 3]
    ]

    face_triangles = []

    for face in faces:

        # Just append the triangles
        if len(face) == 3:
            face_triangles.append(face)

        # Triangulate the quads
        else:
            for triangle in quad_triangles:
                face_triangle = []
                for corner in triangle:
                    face_triangle.append(face[corner])
                face_triangles.append(face_triangle)

    # For each element these are the indices in a pack of 6 nodes, that make
    # up the edges.
    edges = [
        [0, 1],
        [1, 2],
        [2, 0],
        [3, 4],
        [4, 5],
        [5, 3],
        [0, 3],
        [1, 4],
        [2, 5]
    ]

    c3d6_dict['file_name'] = file_name
    c3d6_dict['data_point_size'] = data_point_size
    c3d6_dict['data_point_type'] = data_point_type
    c3d6_dict['points_per_unit'] = points_per_unit

    c3d6_dict['faces'] = faces
    c3d6_dict['face_triangles'] = face_triangles
    c3d6_dict['edges'] = edges

    return c3d6_dict
