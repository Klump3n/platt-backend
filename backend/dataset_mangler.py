#!/usr/bin/env python3
"""
Shape the parsed data, e.g. get the surface or free edges and so on. This is
intended as a module for the dataset parser.

"""
import numpy as np


def model_surface(elements, nodes, elementset):

    # for every element get the faces and the edges of the element
    bulk_faces_and_edges_dict = _dataset_sort_elements_by_faces(elements, elementset)

    # from the faces for every element find those faces that define the
    # boundary (surface) of the dataset
    bulk_faces = bulk_faces_and_edges_dict['bulk_faces']
    bulk_edges = bulk_faces_and_edges_dict['bulk_edges']

    # from the bulk data get the faces on the surface and the unique set of
    # elements for those faces
    surface_faces_dict = _dataset_surface_faces_and_elements(bulk_faces)
    surface_faces = surface_faces_dict['surface_faces']

    # create tets (rather triangles) for the surface
    surface_triangulation_dict = _dataset_triangulate_surface(surface_faces)
    surface_triangulation = surface_triangulation_dict['surface_triangulation']

    # From the edges of every element find the wireframe for the surface of the
    # dataset and the free edges of the dataset, that is edges that give a
    # rough outline of the how the dataset looks
    wireframe_and_free_edges = _dataset_edges(bulk_edges)

    surface_wireframe_lines = wireframe_and_free_edges['wireframe_lines']
    surface_edge_lines = wireframe_and_free_edges['edge_lines']

    # "compress" the data. only keep the nodes from the surface and remove
    # redundant information. create a map for the field data so we can also
    # compress that
    surface_nodes_and_map = _surface_nodes_and_map(nodes, surface_triangulation)

    surface_node_map = surface_nodes_and_map['surface_node_map']
    surface_nodes = surface_nodes_and_map['surface_nodes']
    nodal_field_map = surface_nodes_and_map['nodal_field_map']

    # remap the triangulation dataset
    remapped_surface_triangulation_dict = _remap_surface_triangulation(surface_node_map, surface_triangulation)
    remapped_surface_triangulation = remapped_surface_triangulation_dict['remapped_surface_triangulation']

    remapped_surface_triangles_data = _flatten_nested_lists(remapped_surface_triangulation['surface_triangles'])
    remapped_free_edges_data = _remap_element_data(surface_node_map, surface_edge_lines)
    remapped_wireframe_data = _remap_element_data(surface_node_map, surface_wireframe_lines)

    # generic stuff
    #
    # calculate the center of the dataset
    nodes_center = _nodes_center(surface_nodes)

    remapped_surface_triangles = {
        'type': 'tris',
        'points_per_unit': 3,
        'data': remapped_surface_triangles_data
    }

    remapped_wireframe = {
        'type': 'wireframe',
        'points_per_unit': 2,
        'data': remapped_wireframe_data
    }

    remapped_free_edges = {
        'type': 'free_edges',
        'points_per_unit': 2,
        'data': remapped_free_edges_data
    }

    return_dict = {
        'nodes': surface_nodes,
        'nodes_center': nodes_center,      # center of dataset
        'old_max_node_index': len(surface_node_map),  # safe upper bound for creation of blank field elements

        'triangles': remapped_surface_triangles,
        'wireframe': remapped_wireframe,
        'free_edges': remapped_free_edges,

        # for the creation of the fiels
        'nodal_field_map': nodal_field_map,
        'surface_triangulation': remapped_surface_triangulation  # for getting the elemental fields
    }

    return return_dict


def expand_elemental_fields(elemental_fields, elements, surface_triangulation):

    if elemental_fields is None:
        return None

    surface_triangles = surface_triangulation['surface_triangles']
    surface_element_corners_for_triangle = surface_triangulation['surface_element_corners_for_triangle']
    surface_element_types_for_triangle = surface_triangulation['surface_element_types_for_triangle']
    surface_element_idxs_for_triangle = surface_triangulation['surface_element_idxs_for_triangle']

    fmt_dict = {}
    reshaped_field_data = {}
    res = []

    for element in elements:
        fmt = elements[element]['fmt']

        fmt_dict[element] = {}

        fmt_dict[element]['integration_points'] = fmt['integration_points']
        fmt_dict[element]['node_count'] = fmt['points_per_unit']
        fmt_dict[element]['extrapolation_matrix'] = np.asarray(fmt['int_to_node_matrix'])

        # reshape integration point field data
        field_data = elemental_fields[element]
        len_data_points = len(field_data)
        element_count = int(len_data_points/fmt['integration_points'])

        reshaped_field_data[element] = field_data.reshape(
            element_count, fmt['integration_points'])

    for it, triangle in enumerate(surface_triangles):
        elem_type = surface_element_types_for_triangle[it]
        elem_id = surface_element_idxs_for_triangle[it]
        elem_corners = surface_element_corners_for_triangle[it]

        extrapolation_matrix = fmt_dict[elem_type]['extrapolation_matrix']

        integration_field_data = reshaped_field_data[elem_type][elem_id]
        nodal_field = np.dot(extrapolation_matrix, integration_field_data)

        for jt, corner in enumerate(triangle):
            res.append(nodal_field[elem_corners[jt]])

    return res


def model_surface_fields_nodal(field_map, field_values):
    """
    Extract the surface field values from the bulk.

    Args:
     field_map (array): A list with indices for the bulk field data.
     field_values (array): The field values for the bulk of the dataset.

    Returns:
     dict: The field values for the surface of the dataset.

    """
    remapped_field_data = _remap_index_data(field_map, field_values)

    remapped_field = {
        'type': 'field',
        'points_per_unit': 1,
        'data': remapped_field_data
    }

    return remapped_field


# def model_surface_fields_elemental(field_map, field_values):
def model_surface_fields_elemental(field_values):
    """
    Extract the surface field values from the bulk.

    Args:
     field_map (array): A list with indices for the bulk field data.
     field_values (array): The field values for the bulk of the dataset.

    Returns:
     dict: The field values for the surface of the dataset.

    """
    remapped_field = {
        'type': 'field',
        'points_per_unit': 1,
        'data': field_values
    }

    return remapped_field


def _dataset_sort_elements_by_faces(elements, elementset):
    """
    Sort the elements by the faces the element has.

    """
    faces_array = []
    edges_array = []

    # quick lookup table of sorts
    if elementset:
        lookup_dict = {}
        for element_type in elementset:
            cnt = np.max(elements[element_type]['data'])
            lookup_dict[element_type] = [None]*(cnt + 1)

            elset_data = elementset[element_type]
            for element in elset_data:
                lookup_dict[element_type][element] = element

    # depending on whether or not we select an elementset we pick an iterator
    # set
    iterator_set = elements if (not elementset) else elementset

    # Iterate over all element types (c3d6, c3d8, ...) we find in elements
    for element_type in iterator_set:

        # organization of faces for an element type
        element_data = elements[element_type]['data']  # data
        face_indices = elements[element_type]['fmt']['faces']
        edge_indices = elements[element_type]['fmt']['edges']

        # iteration over individual elements in the dataset
        for element_idx, element in enumerate(element_data):

            # dont add what is not in the elementset
            if elementset and lookup_dict[element_type][element_idx] is None:
                continue
            else:
                # element_hash = hash(tuple(sorted(element)))

                # for each face in the element append a hash of the sorted
                # element and the element
                for face in face_indices:
                    element_face = []
                    for corner in face:
                        element_face.append(element[corner])

                    faces_array.append(
                        [
                            hash(tuple(sorted(element_face))),
                            element_face,
                            face,
                            element_type,
                            element_idx
                        ]
                    )

                for edge in edge_indices:
                    line = sorted([element[edge[0]], element[edge[1]]])

                    edges_array.append(
                        [
                            hash(tuple(line)),
                            line
                        ]
                    )

    sorted_faces_array = sorted(faces_array, key=lambda x: x[0])  # sort by first column
    sorted_edges_array = sorted(edges_array, key=lambda x: x[0])

    element_face_hashes = []
    element_faces = []
    element_corners = []
    element_types = []
    element_idxs = []

    for face in sorted_faces_array:
        element_face_hashes.append(face[0])
        element_faces.append(face[1])
        element_corners.append(face[2])
        element_types.append(face[3])
        element_idxs.append(face[4])

    element_edge_hashes = []
    element_edges = []

    for edge in sorted_edges_array:
        element_edge_hashes.append(edge[0])
        element_edges.append(edge[1])

    return {
        'bulk_faces': {
            'element_face_hashes': element_face_hashes,
            'element_faces': element_faces,
            'element_corners_for_face': element_corners,
            'element_types_for_face': element_types,
            'element_idxs_for_face': element_idxs
        },
        'bulk_edges': {
            'element_edge_hashes': element_edge_hashes,
            'element_edges': element_edges
        }
    }


def _dataset_surface_faces_and_elements(bulk_faces):
    """
    From all faces in the bulk select those who are on the surface.

    Works under the assumption that the faces_hashes are sorted.

    Args:
     bulk_faces (dict): Contains the faces and face hashes for the whole
      dataset.

    Returns:
     dict: The free (surface) faces of the dataset.

    """
    element_face_hashes = bulk_faces['element_face_hashes']
    element_faces = bulk_faces['element_faces']
    element_corners_for_face = bulk_faces['element_corners_for_face']
    element_types_for_face = bulk_faces['element_types_for_face']
    element_idxs_for_face = bulk_faces['element_idxs_for_face']

    # find out, which face occurs how often
    _, unique_face_indices, faces_hash_counts = np.unique(
        element_face_hashes, return_counts=True, return_index=True)

    # we want the surfaces that occur only once
    surface_hash_indices = np.where(faces_hash_counts == 1)[0]

    # for the hashes that occur once we append the corresponding faces to
    # a list with all free faces. those faces are pointing outward
    surface_faces = [None]*len(surface_hash_indices)
    surface_element_corners_for_face = [None]*len(surface_hash_indices)
    surface_element_types_for_face = [None]*len(surface_hash_indices)
    surface_element_idxs_for_face = [None]*len(surface_hash_indices)

    for it, index in enumerate(surface_hash_indices):  # PARALLELIZE ME

        surface_faces[it] = element_faces[unique_face_indices[index]]
        surface_element_corners_for_face[it] = element_corners_for_face[unique_face_indices[index]]
        surface_element_types_for_face[it] = element_types_for_face[unique_face_indices[index]]
        surface_element_idxs_for_face[it] = element_idxs_for_face[unique_face_indices[index]]

    return {
        'surface_faces': {
            'surface_faces': surface_faces,
            'element_corners_for_face': surface_element_corners_for_face,
            'element_types_for_face': surface_element_types_for_face,
            'element_idxs_for_face': surface_element_idxs_for_face
        }
    }


def _dataset_triangulate_surface(surface_faces):
    """
    Generate tetraeders for the free faces.

    Args:
     free_faces (dict): The free (outward pointing) faces of the dataset.
      free_faces = {'free_faces': [ [face1], [face2], ...]}

    Returns:
     tets (array): The outward facing tetraeders.

    """
    surface_faces_array = surface_faces['surface_faces']
    surface_element_corners_for_face = surface_faces['element_corners_for_face']
    surface_element_types_for_face = surface_faces['element_types_for_face']
    surface_element_idxs_for_face = surface_faces['element_idxs_for_face']

    surface_triangles = []
    surface_element_corners_for_triangle = []
    surface_element_types_for_triangle = []
    surface_element_idxs_for_triangle = []

    for it, face in enumerate(surface_faces_array):
        # just append the face (which is already a triangle)
        if len(face) == 3:
            surface_triangles.append(face)
            surface_element_corners_for_triangle.append(
                surface_element_corners_for_face[it])
            surface_element_types_for_triangle.append(
                surface_element_types_for_face[it])
            surface_element_idxs_for_triangle.append(
                surface_element_idxs_for_face[it])

        # a quad has to be split up into two triangles
        if len(face) == 4:
            # triangle one (0, 1, 2)
            surface_triangles.append([face[0], face[1], face[2]])
            corner = surface_element_corners_for_face[it]
            surface_element_corners_for_triangle.append(
                [corner[0], corner[1], corner[2]])
            surface_element_types_for_triangle.append(
                surface_element_types_for_face[it])
            surface_element_idxs_for_triangle.append(
                surface_element_idxs_for_face[it])

            # triangle two (0, 2, 3)
            surface_triangles.append([face[0], face[2], face[3]])
            corner = surface_element_corners_for_face[it]
            surface_element_corners_for_triangle.append(
                [corner[0], corner[2], corner[3]])
            surface_element_types_for_triangle.append(
                surface_element_types_for_face[it])
            surface_element_idxs_for_triangle.append(
                surface_element_idxs_for_face[it])

    return {
        'surface_triangulation': {
            'surface_triangles': surface_triangles,
            'surface_element_corners_for_triangle': surface_element_corners_for_triangle,
            'surface_element_types_for_triangle': surface_element_types_for_triangle,
            'surface_element_idxs_for_triangle': surface_element_idxs_for_triangle
        }
    }


def _dataset_edges(bulk_edges):
    """
    For for edges in the dataset we build a wireframe and the datasets corner
    edges.

    Args:
     bulk_edges (dict): The edges for every element in the dataset.

    Returns:
     dict: The free edges and the wireframe for the surface of the dataset.

    """
    edges = bulk_edges['element_edges']
    edges_hashes = bulk_edges['element_edge_hashes']

    # find out which edges occur how often
    _, unique_indices, edges_hash_counts = np.unique(
        edges_hashes, return_counts=True, return_index=True)

    # edges that occur once are free edges
    free_edges_hash_indices = np.where(edges_hash_counts == 1)[0]

    # edges that occur twice are wireframe
    wireframe_hash_indices = np.where(edges_hash_counts == 2)[0]

    num_free_edges = len(free_edges_hash_indices)
    num_inner_edges = len(wireframe_hash_indices)

    free_edges_lines = [None]*num_free_edges
    wireframe_edges = [None]*num_inner_edges

    for it, index in enumerate(free_edges_hash_indices):  # PARALLELIZE ME
        free_edge = edges[unique_indices[index]]
        free_edges_lines[it] = free_edge

    for it, index in enumerate(wireframe_hash_indices):  # PARALLELIZE ME
        wireframe_edge = edges[unique_indices[index]]
        wireframe_edges[it] = wireframe_edge

    return {
        'edge_lines': free_edges_lines,
        'wireframe_lines': wireframe_edges
    }


def _surface_nodes_and_map(nodes, surface_triangulation):
    """
    Return a map that points from the indices for the surface to new
    consecutive indices.

    Args:
     nodes (dict): The nodes of the bulk of the dataset.
     free_faces (dict): The surface faces of the dataset.

    Returns:
     dict: The compressed nodes on the surface, a map to construct the surface
      from the bulk and a map to construct a compressed surface field.

    """
    surface_triangles = surface_triangulation['surface_triangles']

    # find a unique set of indices
    flat_surface_triangles = _flatten_nested_lists(surface_triangles)

    max_element_num = max(flat_surface_triangles)

    unique_surface_nodes = np.unique(flat_surface_triangles)

    nodes_data = nodes['data']

    # create a map between the old indices and the new indices
    surface_nodes = []
    surface_node_map = [None]*(max_element_num + 1)

    # a index map for the field values
    nodal_field_map = []

    for index, value in enumerate(unique_surface_nodes):
        surface_node_map[value] = index

        # also create a list with only the nodes we need for the surface
        surface_nodes.append(nodes_data[value])
        nodal_field_map.append(value)

    flat_remapped_nodes = _flatten_nested_lists(surface_nodes)

    remapped_nodes = {
        'type': 'surface_nodes',
        'points_per_unit': 3,
        'data': flat_remapped_nodes
    }

    return {
        'surface_node_map': surface_node_map,
        'surface_nodes': remapped_nodes,
        'nodal_field_map': nodal_field_map
    }


def _remap_surface_triangulation(surface_node_map, surface_triangulation):
    """
    Remap the surface triangles.

    """
    surface_triangles = surface_triangulation['surface_triangles']

    remapped_surface_triangles = []

    for triangle in surface_triangles:
        new_triangle = []
        for corner_idx in triangle:
            new_triangle.append(surface_node_map[corner_idx])
        remapped_surface_triangles.append(new_triangle)

    surface_triangulation['surface_triangles'] = remapped_surface_triangles
    remapped_surface_triangulation = surface_triangulation

    return {
        'remapped_surface_triangulation': remapped_surface_triangulation
    }


def _surface_nodes_and_map_nodal(nodes, surface_triangles):
    """
    Return a map that points from the indices for the surface to new
    consecutive indices.

    Args:
     nodes (dict): The nodes of the bulk of the dataset.
     free_faces (dict): The surface faces of the dataset.

    Returns:
     dict: The compressed nodes on the surface, a map to construct the surface
      from the bulk and a map to construct a compressed surface field.

    """
    # find a unique set of indices
    flat_faces = _flatten_nested_lists(surface_triangles)

    max_element_num = max(flat_faces)

    unique_indices = np.unique(flat_faces)
    # unique_indices = np.unique(faces_data)

    nodes_data = nodes['data']

    # create a map between the old indices and the new indices
    remapped_nodes = []
    surface_node_map = [None]*(max_element_num + 1)

    # a index map for the field values
    field_map = []

    for index, value in enumerate(unique_indices):
        surface_node_map[value] = index
        # also create a list with only the nodes we need for the surface
        remapped_nodes.append(nodes_data[value])
        field_map.append(value)

    flat_remapped_nodes = _flatten_nested_lists(remapped_nodes)

    remapped_nodes = {
        'type': 'surface_nodes',
        'points_per_unit': 3,
        'data': flat_remapped_nodes
    }

    return {
        'surface_node_map': surface_node_map,
        'field_map': field_map,
        'remapped_nodes': remapped_nodes
    }


def _surface_nodes_and_map_elemental(
        nodes,
        surface_triangles,
        surface_triangle_types,
        surface_triangle_idxs
):
    """
    Return a map that points from the indices for the surface to new
    consecutive indices.

    Args:
     nodes (dict): The nodes of the bulk of the dataset.
     free_faces (dict): The surface faces of the dataset.

    Returns:
     dict: The compressed nodes on the surface, a map to construct the surface
      from the bulk and a map to construct a compressed surface field.

    """
    # find a unique set of indices
    flat_faces = _flatten_nested_lists(surface_triangles)

    max_element_num = max(flat_faces)

    nodes_data = nodes['data']

    # create a map between the old indices and the new indices
    remapped_nodes = []
    surface_node_map = [None]*(max_element_num + 1)

    # a index map for the field values
    field_map = []

    triangle_types = []
    triangle_idxs = []

    # allocate some space
    unique_types = np.unique(surface_triangle_types)
    combn = {}
    for unique_type in unique_types:
        combn[unique_type] = []

    for index, value in enumerate(flat_faces):
        surface_node_map[value] = index
        # also create a list with only the nodes we need for the surface
        remapped_nodes.append(nodes_data[value])
        field_map.append(value)

        # flat faces will be three times as long as surface_triangle_{types/idxs}
        type_id_index = int(index/3)
        triangle_types.append(surface_triangle_types[type_id_index])
        triangle_idxs.append(surface_triangle_idxs[type_id_index])

        combn[surface_triangle_types[type_id_index]].append(value)

    flat_remapped_nodes = _flatten_nested_lists(remapped_nodes)

    remapped_nodes = {
        'type': 'surface_nodes',
        'points_per_unit': 3,
        'data': flat_remapped_nodes
    }

    return {
        'surface_node_map': surface_node_map,
        'field_map': field_map,
        'triangle_types': triangle_types,
        'triangle_idxs': triangle_idxs,
        'remapped_nodes': remapped_nodes,
        'field_map_combined': combn
    }


def _flatten_nested_lists(container):
    """
    Flatten arbitrarily nested lists.

    From https://stackoverflow.com/a/10824420

    Args:
     container (tuple or list): The tuple or list we want to flatten.

    Returns:
     list: A flat list.

    """
    def flatten(container):
        for i in container:
            if isinstance(i, (list, tuple, np.ndarray)):
                for j in flatten(i):
                    yield j
            else:
                yield i

    return list(flatten(container))


def _remap_element_data(surface_node_map, data):
    """
    Reassign indices of some data based on the surface node map.

    This is to compress the data for transmission to the frontend.

    Args:
     surface_node_map (array): A map for extracting surface nodes from bulk
      nodes.
     data (array): Some element data from which we want to extrapolate the
      surface.

    Returns:
     array: The surface of data.

    """
    # flatten data
    flat_data = _flatten_nested_lists(data)

    remapped_data = []
    for data_point in flat_data:
        remapped_data.append(surface_node_map[data_point])

    return remapped_data


def _remap_index_data(field_map, data):
    """
    Remap data based on indices.

    Args:
     field_map (array): A map for extracting surface field values from bulk
      field values.
     data (array): Some field data from which we want to extrapolate the
      surface values.

    Returns:
     array: The surface of data.

    """
    remapped_data = []

    for index in field_map:
        remapped_data.append(data[index])

    return remapped_data


def _nodes_center(nodes_dict):
    """
    Return the center of the mesh.

    Assume that nodes is a list with length divisible by 3.
    This effectively calculates the average value of the x, y and z coordinates
    of the nodes.

    Args:
     nodes_dict (dict): A dictionary containing the nodes,
      nodes_dict = { ... , 'data': [x1, y1, z1, x2, ...], ... }.

    Returns:
     array: The average values of the x, y and z coordinates of
      nodes_dict['data'].

    """
    nodes = nodes_dict['data']
    x = nodes[0::3]
    y = nodes[1::3]
    z = nodes[2::3]

    return [np.mean(x), np.mean(y), np.mean(z)]
