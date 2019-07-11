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

def nodes_ma():
    """
    The node binary format for mechanical nodes files.

    Same as nodes, just different file.

    """
    nodes_dict = {}

    file_name = 'nodes_ma.bin'

    data_point_size = 8    # 8 bytes of ...
    data_point_type = 'd'     # ... doubles
    points_per_unit = 3  # 3 coords per node

    nodes_dict['file_name'] = file_name
    nodes_dict['data_point_size'] = data_point_size
    nodes_dict['data_point_type'] = data_point_type
    nodes_dict['points_per_unit'] = points_per_unit

    return nodes_dict

def elementset():
    """
    The elementset binary format.

    """
    elementset_dict = {}

    file_name = 'NAME.elset.ELEMENT_TYPE.bin'

    data_point_size = 4    # 4 bytes of ...
    data_point_type = 'i'     # ... integers
    points_per_unit = 1  # 1 coord per element

    elementset_dict['file_name'] = file_name
    elementset_dict['data_point_size'] = data_point_size
    elementset_dict['data_point_type'] = data_point_type
    elementset_dict['points_per_unit'] = points_per_unit

    return elementset_dict


def nodal_fields():
    """
    The binary format for nodal fields.

    """

    nodal_field_dict = {}

    nodal_dir = 'no'

    data_point_size = 8    # 8 bytes of ...
    data_point_type = 'd'     # ... doubles
    points_per_unit = 1  # 1 data point per unit.

    nodal_field_dict['data_dir'] = nodal_dir
    nodal_field_dict['data_point_size'] = data_point_size
    nodal_field_dict['data_point_type'] = data_point_type
    nodal_field_dict['points_per_unit'] = points_per_unit

    return nodal_field_dict


def elemental_fields():
    """
    The binary format for elemental fields.

    """

    elemental_field_dict = {}

    elemental_dir = 'eo'

    data_point_size = 8    # 8 bytes of ...
    data_point_type = 'd'     # ... doubles
    points_per_unit = 1  # 1 data point per unit.

    elemental_field_dict['data_dir'] = elemental_dir
    elemental_field_dict['data_point_size'] = data_point_size
    elemental_field_dict['data_point_type'] = data_point_type
    elemental_field_dict['points_per_unit'] = points_per_unit

    return elemental_field_dict

def valid_element_types():
    """
    Return a list with the valid element type names.

    """
    return ["c3d6", "c3d8", "c3d15", "c3d20"]

def c3d20():
    """
    The c3d20 binary format.

    We parse 4 bytes of integers that are grouped into packs of 20, because an
    element in this format consists of 20 nodes.

    """
    c3d20_dict = {}

    file_name = 'elements.c3d20.bin'

    nodes_file = "nodes_ma"

    data_point_size = 4    # 4 bytes of ...
    data_point_type = 'i'     # ... integers
    points_per_unit = 20  # 20 points per element

    # for extrapolation of fields from integration points to nodes
    integration_points = 8

    extrapolation_matrix = [
        [ 0.87580713, -0.84681697,  0.52863515, -0.84681697, -0.84681697,  0.52863515, -0.19398895,  0.52863515],
        [-0.84681697,  0.87580713, -0.84681697,  0.52863515,  0.52863515, -0.84681697,  0.52863515, -0.19398895],
        [ 0.52863515, -0.84681697,  0.87580713, -0.84681697, -0.19398895,  0.52863515, -0.84681697,  0.52863515],
        [-0.84681697,  0.52863515, -0.84681697,  0.87580713,  0.52863515, -0.19398895,  0.52863515, -0.84681697],
        [-0.84681697,  0.52863515, -0.19398895,  0.52863515,  0.87580713, -0.84681697,  0.52863515, -0.84681697],
        [ 0.52863515, -0.84681697,  0.52863515, -0.19398895, -0.84681697,  0.87580713, -0.84681697,  0.52863515],
        [-0.19398895,  0.52863515, -0.84681697,  0.52863515,  0.52863515, -0.84681697,  0.87580713, -0.84681697],
        [ 0.52863515, -0.19398895,  0.52863515, -0.84681697, -0.84681697,  0.52863515, -0.84681697,  0.87580713],
        [ 0.85111057,  0.85111057, -0.45454545, -0.45454545, -0.45454545, -0.45454545,  0.23979852,  0.23979852],
        [-0.45454545,  0.85111057,  0.85111057, -0.45454545,  0.23979852, -0.45454545, -0.45454545,  0.23979852],
        [-0.45454545, -0.45454545,  0.85111057,  0.85111057,  0.23979852,  0.23979852, -0.45454545, -0.45454545],
        [ 0.85111057, -0.45454545, -0.45454545,  0.85111057, -0.45454545,  0.23979852,  0.23979852, -0.45454545],
        [-0.45454545, -0.45454545,  0.23979852,  0.23979852,  0.85111057,  0.85111057, -0.45454545, -0.45454545],
        [ 0.23979852, -0.45454545, -0.45454545,  0.23979852, -0.45454545,  0.85111057,  0.85111057, -0.45454545],
        [ 0.23979852,  0.23979852, -0.45454545, -0.45454545, -0.45454545, -0.45454545,  0.85111057,  0.85111057],
        [-0.45454545,  0.23979852,  0.23979852, -0.45454545,  0.85111057, -0.45454545, -0.45454545,  0.85111057],
        [ 0.85111057, -0.45454545,  0.23979852, -0.45454545,  0.85111057, -0.45454545,  0.23979852, -0.45454545],
        [-0.45454545,  0.85111057, -0.45454545,  0.23979852, -0.45454545,  0.85111057, -0.45454545,  0.23979852],
        [ 0.23979852, -0.45454545,  0.85111057, -0.45454545,  0.23979852, -0.45454545,  0.85111057, -0.45454545],
        [-0.45454545,  0.23979852, -0.45454545,  0.85111057, -0.45454545,  0.23979852, -0.45454545,  0.85111057]
    ]

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

    c3d20_dict['file_name'] = file_name
    c3d20_dict['data_point_size'] = data_point_size
    c3d20_dict['data_point_type'] = data_point_type
    c3d20_dict['points_per_unit'] = points_per_unit

    c3d20_dict['integration_points'] = integration_points
    c3d20_dict['int_to_node_matrix'] = extrapolation_matrix

    c3d20_dict['faces'] = faces
    c3d20_dict['face_triangles'] = face_triangles
    c3d20_dict['edges'] = edges

    return c3d20_dict


def c3d15():
    """
    The c3d15 binary format.

    We parse 4 bytes of integers that are grouped into packs of 15, because an
    element in this format consists of 15 nodes.

    """
    c3d15_dict = {}

    file_name = 'elements.c3d15.bin'

    nodes_file = "nodes_ma"

    data_point_size = 4    # 4 bytes of ...
    data_point_type = 'i'     # ... integers
    points_per_unit = 15  # 15 points per element

    # for extrapolation of fields from integration points to nodes
    integration_points = 9

    extrapolation_matrix = [
        [ 1.62697871, -0.67460046, -0.67460046, -1.16296296,  0.3037037 ,  0.3037037 ,  0.33598426, -0.02910324, -0.02910324],
        [-0.67460046,  1.62697871, -0.67460046,  0.3037037 , -1.16296296,  0.3037037 , -0.02910324,  0.33598426, -0.02910324],
        [-0.67460046, -0.67460046,  1.62697871,  0.3037037 ,  0.3037037 , -1.16296296, -0.02910324, -0.02910324,  0.33598426],
        [ 0.33598426, -0.02910324, -0.02910324, -1.16296296,  0.3037037 ,  0.3037037 ,  1.62697871, -0.67460046, -0.67460046],
        [-0.02910324,  0.33598426, -0.02910324,  0.3037037 , -1.16296296,  0.3037037 , -0.67460046,  1.62697871, -0.67460046],
        [-0.02910324, -0.02910324,  0.33598426,  0.3037037 ,  0.3037037 , -1.16296296, -0.67460046, -0.67460046,  1.62697871],
        [ 1.20458102,  1.20458102, -0.93033148, -0.4       , -0.4       ,  0.13333333,  0.12875231,  0.12875231, -0.06966852],
        [-0.93033148,  1.20458102,  1.20458102,  0.13333333, -0.4       , -0.4       , -0.06966852,  0.12875231,  0.12875231],
        [ 1.20458102, -0.93033148,  1.20458102, -0.4       ,  0.13333333, -0.4       ,  0.12875231, -0.06966852,  0.12875231],
        [ 0.12875231,  0.12875231, -0.06966852, -0.4       , -0.4       ,  0.13333333,  1.20458102,  1.20458102, -0.93033148],
        [-0.06966852,  0.12875231,  0.12875231,  0.13333333, -0.4       , -0.4       , -0.93033148,  1.20458102,  1.20458102],
        [ 0.12875231, -0.06966852,  0.12875231, -0.4       ,  0.13333333, -0.4       ,  1.20458102, -0.93033148,  1.20458102],
        [-0.40740741, -0.07407407, -0.07407407,  1.61481481, -0.25185185, -0.25185185, -0.40740741, -0.07407407, -0.07407407],
        [-0.07407407, -0.40740741, -0.07407407, -0.25185185,  1.61481481, -0.25185185, -0.07407407, -0.40740741, -0.07407407],
        [-0.07407407, -0.07407407, -0.40740741, -0.25185185, -0.25185185,  1.61481481, -0.07407407, -0.07407407, -0.40740741]
    ]

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
        [0, 6, 1],
        [1, 7, 2],
        [2, 8, 0],

        [3, 9, 4],
        [4, 10, 5],
        [5, 11, 3],

        [0, 12, 3],
        [1, 13, 4],
        [2, 14, 5]
    ]

    c3d15_dict['file_name'] = file_name
    c3d15_dict['data_point_size'] = data_point_size
    c3d15_dict['data_point_type'] = data_point_type
    c3d15_dict['points_per_unit'] = points_per_unit

    c3d15_dict['integration_points'] = integration_points
    c3d15_dict['int_to_node_matrix'] = extrapolation_matrix

    c3d15_dict['faces'] = faces
    c3d15_dict['face_triangles'] = face_triangles
    c3d15_dict['edges'] = edges

    return c3d15_dict

def c3d8():
    """
    The c3d8 binary format.

    We parse 4 bytes of integers that are grouped into packs of 8, because an
    element in this format consists of 8 nodes.

    """
    c3d8_dict = {}

    file_name = 'elements.c3d8.bin'

    nodes_file = "nodes"

    data_point_size = 4    # 4 bytes of ...
    data_point_type = 'i'     # ... integers
    points_per_unit = 8  # 8 points per element

    # for extrapolation of fields from integration points to nodes
    integration_points = 8

    extrapolation_matrix = [
        [ 2.54903811, -0.6830127 ,  0.1830127 , -0.6830127 , -0.6830127 ,  0.1830127 , -0.04903811,  0.1830127 ],
        [-0.6830127 ,  2.54903811, -0.6830127 ,  0.1830127 ,  0.1830127 , -0.6830127 ,  0.1830127 , -0.04903811],
        [ 0.1830127 , -0.6830127 ,  2.54903811, -0.6830127 , -0.04903811,  0.1830127 , -0.6830127 ,  0.1830127 ],
        [-0.6830127 ,  0.1830127 , -0.6830127 ,  2.54903811,  0.1830127 , -0.04903811,  0.1830127 , -0.6830127 ],
        [-0.6830127 ,  0.1830127 , -0.04903811,  0.1830127 ,  2.54903811, -0.6830127 ,  0.1830127 , -0.6830127 ],
        [ 0.1830127 , -0.6830127 ,  0.1830127 , -0.04903811, -0.6830127 ,  2.54903811, -0.6830127 ,  0.1830127 ],
        [-0.04903811,  0.1830127 , -0.6830127 ,  0.1830127 ,  0.1830127 , -0.6830127 ,  2.54903811, -0.6830127 ],
        [ 0.1830127 , -0.04903811,  0.1830127 , -0.6830127 , -0.6830127 ,  0.1830127 , -0.6830127 ,  2.54903811]
    ]

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

    c3d8_dict['integration_points'] = integration_points
    c3d8_dict['int_to_node_matrix'] = extrapolation_matrix

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

    nodes_file = "nodes"

    data_point_size = 4    # 4 bytes of ...
    data_point_type = 'i'     # ... integers
    points_per_unit = 6  # 8 points per element

    # for extrapolation of fields from integration points to nodes
    integration_points = 9

    extrapolation_matrix = [
        [ 1.63138426, -0.32627685, -0.32627685,  0.55555556, -0.11111111, -0.11111111, -0.52027315,  0.10405463,  0.10405463],
        [-0.32627685,  1.63138426, -0.32627685, -0.11111111,  0.55555556, -0.11111111,  0.10405463, -0.52027315,  0.10405463],
        [-0.32627685, -0.32627685,  1.63138426, -0.11111111, -0.11111111,  0.55555556,  0.10405463,  0.10405463, -0.52027315],
        [-0.52027315,  0.10405463,  0.10405463,  0.55555556, -0.11111111, -0.11111111,  1.63138426, -0.32627685, -0.32627685],
        [ 0.10405463, -0.52027315,  0.10405463, -0.11111111,  0.55555556, -0.11111111, -0.32627685,  1.63138426, -0.32627685],
        [ 0.10405463,  0.10405463, -0.52027315, -0.11111111, -0.11111111,  0.55555556, -0.32627685, -0.32627685,  1.63138426]
    ]

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

    c3d6_dict['integration_points'] = integration_points
    c3d6_dict['int_to_node_matrix'] = extrapolation_matrix

    c3d6_dict['faces'] = faces
    c3d6_dict['face_triangles'] = face_triangles
    c3d6_dict['edges'] = edges

    return c3d6_dict

def skin():
    """
    Return the format for a skin.

    Parse a four byte integer that contains two different numbers.

    number_mask  = int("00000011111111111111111111111111", 2)
    face_id_mask = int("11111100000000000000000000000000", 2)

    # one integer
    word = struct.unpack("<1I".format(datacount), data) 

    # get the number by and-ing the number mask
    number = word & number_mask

    # get the face id by and-ing the face id mask and bit shifting by 26 bits
    face_id = (word & face_id_mask) >> 26

    """
    skin_dict = {}

    file_name = 'skin.c3d.bin'

    data_point_size = 4    # 4 bytes of ...
    data_point_type = 'i'     # ... integers
    points_per_unit = 1  # 1 point per element

    number_mask  = int("00000011111111111111111111111111", 2)
    face_id_mask = int("11111100000000000000000000000000", 2)
    face_id_bitshift_right_by = 26

    skin_dict['file_name'] = file_name
    skin_dict['data_point_size'] = data_point_size
    skin_dict['data_point_type'] = data_point_type
    skin_dict['points_per_unit'] = points_per_unit

    skin_dict["number_mask"] = number_mask
    skin_dict["face_id_mask"] = face_id_mask
    skin_dict["face_id_bitshift_right_by"] = face_id_bitshift_right_by

    return skin_dict
