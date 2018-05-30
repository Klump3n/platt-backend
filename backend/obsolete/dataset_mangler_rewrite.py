#!/usr/bin/env python3
"""
Shape the parsed data, e.g. get the surface or free edges and so on. This is
intended as a module for the dataset parser.

"""
import numpy as np
# import backend.binary_formats as binary_formats


def model_surface(elements, nodes):

    # for every element get the faces and the edges of the element
    bulk_faces_and_edges = _dataset_sort_elements_by_faces(elements)

    # from the faces for every element find those faces that define the
    # boundary (surface) of the dataset
    bulk_faces = bulk_faces_and_edges['faces']
    bulk_elements_to_faces = bulk_faces_and_edges['elements_to_faces']
    bulk_edges = bulk_faces_and_edges['edges']

    # from the bulk data get the faces on the surface and the unique set of
    # elements for those faces
    surface_faces_and_elements = _dataset_surface_faces_and_elements(
        bulk_faces, bulk_elements_to_faces)

    surface_faces = surface_faces_and_elements['surface_faces']
    surface_face_types = surface_faces_and_elements['surface_face_types']
    surface_face_element_idxs = surface_faces_and_elements['surface_face_element_idxs']
    surface_elements = surface_faces_and_elements['surface_elements']

    # create tets (rather triangles) for the surface
    surface_triangulation_data = _dataset_triangulate_surface(surface_faces, surface_face_types, surface_face_element_idxs)

    surface_triangulation = surface_triangulation_data['triangulation']
    surface_triangulation_type = surface_triangulation_data['element_types']
    surface_triangulation_idx = surface_triangulation_data['element_idxs']

    # From the edges of every element find the wireframe for the surface of the
    # dataset and the free edges of the dataset, that is edges that give a
    # rough outline of the how the dataset looks
    wireframe_and_free_edges = _dataset_edges(bulk_edges)

    surface_wireframe_lines = wireframe_and_free_edges['wireframe_lines']
    surface_edge_lines = wireframe_and_free_edges['edge_lines']

    # "compress" the data. only keep the nodes from the surface and remove
    # redundant information. create a map for the field data so we can also
    # compress that
    nodal_surface_nodes_and_map = _surface_nodes_and_map_nodal(
        nodes, surface_triangulation)

    nodal_surface_node_map = nodal_surface_nodes_and_map['surface_node_map']
    nodal_remapped_nodes = nodal_surface_nodes_and_map['remapped_nodes']
    nodal_field_map = nodal_surface_nodes_and_map['field_map']

    # "compress" the tetraeders on the surface
    # does not have to be separated by type
    nodal_remapped_tris_data = _remap_element_data(nodal_surface_node_map, surface_triangulation)

    nodal_remapped_tris = {
        'type': 'tris',
        'points_per_unit': 3,
        'data': nodal_remapped_tris_data
    }

    # "compress" the free edges of the dataset
    nodal_remapped_free_edges_data = _remap_element_data(
        nodal_surface_node_map, surface_edge_lines)

    nodal_remapped_free_edges = {
        'type': 'free_edges',
        'points_per_unit': 2,
        'data': nodal_remapped_free_edges_data
    }

    # compress the wireframe of the dataset
    nodal_remapped_wireframe_data = _remap_element_data(
        nodal_surface_node_map, surface_wireframe_lines)

    nodal_remapped_wireframe = {
        'type': 'wireframe',
        'points_per_unit': 2,
        'data': nodal_remapped_wireframe_data
    }

    # elemental stuff
    elemental_surface_nodes_and_map = _surface_nodes_and_map_elemental(
        nodes, surface_triangulation, surface_triangulation_type, surface_triangulation_idx)

    elemental_surface_node_map = elemental_surface_nodes_and_map['surface_node_map']
    elemental_remapped_nodes = elemental_surface_nodes_and_map['remapped_nodes']
    elemental_field_map = elemental_surface_nodes_and_map['field_map']
    elemental_triangle_types = elemental_surface_nodes_and_map['triangle_types']
    elemental_triangle_idxs = elemental_surface_nodes_and_map['triangle_idxs']
    elemental_field_map_combined = elemental_surface_nodes_and_map['field_map_combined']

    # "compress" the tetraeders on the surface
    elemental_remapped_tris_data = _remap_element_data(elemental_surface_node_map, surface_triangulation)

    elemental_remapped_tris = {
        'type': 'tris',
        'points_per_unit': 3,
        'data': elemental_remapped_tris_data
    }

    # "compress" the free edges of the dataset
    elemental_remapped_free_edges_data = _remap_element_data(
        elemental_surface_node_map, surface_edge_lines)

    elemental_remapped_free_edges = {
        'type': 'free_edges',
        'points_per_unit': 2,
        'data': elemental_remapped_free_edges_data
    }

    # compress the wireframe of the dataset
    elemental_remapped_wireframe_data = _remap_element_data(
        elemental_surface_node_map, surface_wireframe_lines)

    elemental_remapped_wireframe = {
        'type': 'wireframe',
        'points_per_unit': 2,
        'data': elemental_remapped_wireframe_data
    }

    # generic stuff
    #
    # calculate the center of the dataset
    nodes_center = _nodes_center(nodal_remapped_nodes)

    print('nodal triangles {}'.format(len(nodal_remapped_tris['data'])))
    print('elemental triangles {}'.format(len(elemental_remapped_tris['data'])))

    print(len(nodal_remapped_nodes['data']), len(elemental_remapped_nodes['data']))

    return {
        'nodal': {
            'nodes': nodal_remapped_nodes,              # the compressed nodes
            'node_count': len(nodal_surface_node_map),  # how many nodes on the surface
            'nodes_center': nodes_center,      # center of dataset

            'tris': nodal_remapped_tris,   # the compressed surface tris

            'free_edges': nodal_remapped_free_edges,  # compressed free edges
            'wireframe': nodal_remapped_wireframe,     # compressed wireframe

            'field_map': nodal_field_map  # the compression map for the fields
        },
        'elemental': {
            'nodes': elemental_remapped_nodes,              # the compressed nodes
            'node_count': len(elemental_surface_node_map),  # how many nodes on the surface
            'nodes_center': nodes_center,      # center of dataset

            'tris': elemental_remapped_tris,   # the compressed surface tris

            'free_edges': elemental_remapped_free_edges,  # compressed free edges
            'wireframe': elemental_remapped_wireframe,     # compressed wireframe

            'surface_elements': surface_elements,  # the unique elements on the surface
            'field_map': elemental_field_map,  # the compression map for the fields
            'field_map_combined': elemental_field_map_combined,  # the compression map for the fields
            'surface_triangle_element_types': elemental_triangle_types,
            'surface_triangle_element_idxs': elemental_triangle_idxs
        }
    }



def expand_elemental_fields(elemental_fields, elements, surface_elements):

    if elemental_fields is None:
        return None

    extrapolated_fields = {}

    for element in elements:
        fmt = elements[element]['fmt']
        integration_points = fmt['integration_points']
        node_count = fmt['points_per_unit']

        extrapolation_matrix = np.asarray(fmt['int_to_node_matrix'])

        # reshape integration point field data
        field_data = elemental_fields[element]
        len_data_points = len(field_data)
        element_count = int(len_data_points/integration_points)
        reshaped_field_data = field_data.reshape(
            element_count, integration_points)

        surface_element_indices = surface_elements[element]['element_idxs']
        print(len(surface_element_indices), min(surface_element_indices), max(surface_element_indices))

        extrapolated_field = [None]*(element_count*node_count + 1)
        for element_id in surface_element_indices:

            integration_field = reshaped_field_data[element_id]
            nodal_field = np.dot(extrapolation_matrix, integration_field)

            array_indices = elements[element]['data'][element_id]
            for it, index in enumerate(array_indices):
                extrapolated_field[index] = nodal_field[it]

        extrapolated_fields[element] = extrapolated_field

    return extrapolated_fields


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


def model_surface_fields_elemental(field_map, field_values):
    """
    Extract the surface field values from the bulk.

    Args:
     field_map (array): A list with indices for the bulk field data.
     field_values (array): The field values for the bulk of the dataset.

    Returns:
     dict: The field values for the surface of the dataset.

    """
    # for elem_type in field_values:
    #     print('map {} {}'.format(elem_type, len(field_map[elem_type])))
    #     print('values {} {}'.format(elem_type, len(field_values[elem_type])))
    print('pre remap')
    remapped_field_data = []
    for elem_type in field_values:
        remapped_field_data = remapped_field_data + _remap_index_data(field_map[elem_type], field_values[elem_type])
    print('post remap')

    remapped_field = {
        'type': 'field',
        'points_per_unit': 1,
        'data': remapped_field_data
    }

    return remapped_field


def _dataset_sort_elements_by_faces(elements):
    """
    Sort the elements by the faces the element has.

    """
    faces_array = []
    edges_array = []

    # Iterate over all element types (c3d6, c3d8, ...) we find in elements
    for element_type in elements:

        # organization of faces for an element type
        element_data = elements[element_type]['data']  # data
        face_indices = elements[element_type]['fmt']['faces']
        edge_indices = elements[element_type]['fmt']['edges']

        # iteration over individual elements in the dataset
        for element_idx, element in enumerate(element_data):

            element_hash = hash(tuple(sorted(element)))

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
                        element_hash,
                        element_type,
                        element,
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
    element_hashes = []
    element_types = []
    elements = []
    element_idxs = []

    for face in sorted_faces_array:
        element_face_hashes.append(face[0])
        element_faces.append(face[1])
        element_hashes.append(face[2])
        element_types.append(face[3])
        elements.append(face[4])
        element_idxs.append(face[5])

    element_edge_hashes = []
    element_edges = []

    for edge in sorted_edges_array:
        element_edge_hashes.append(edge[0])
        element_edges.append(edge[1])

    return {
        'faces': {
            'element_face_hashes': element_face_hashes,
            'element_faces': element_faces
        },
        'elements_to_faces': {  # this is intended as additional information for the faces
            'element_hashes': element_hashes,
            'element_types': element_types,
            'elements': elements,
            'element_idxs': element_idxs
        },
        'edges': {
            'element_edge_hashes': element_edge_hashes,
            'element_edges': element_edges
        }
    }


def _dataset_surface_faces_and_elements(faces, elements_to_faces):
    """
    From all faces in the bulk select those who are on the surface.

    Works under the assumption that the faces_hashes are sorted.

    Args:
     bulk_faces (dict): Contains the faces and face hashes for the whole
      dataset.

    Returns:
     dict: The free (surface) faces of the dataset.

    """
    element_face_hashes = faces['element_face_hashes']
    element_faces = faces['element_faces']

    element_hashes = elements_to_faces['element_hashes']
    element_types = elements_to_faces['element_types']
    elements = elements_to_faces['elements']
    element_idxs = elements_to_faces['element_idxs']

    # find out, which face occurs how often
    _, unique_face_indices, faces_hash_counts = np.unique(
        element_face_hashes, return_counts=True, return_index=True)

    # we want the surfaces that occur only once
    surface_hash_indices = np.where(faces_hash_counts == 1)[0]

    # for the hashes that occur once we append the corresponding faces to
    # a list with all free faces. those faces are pointing outward
    surface_faces = [None]*len(surface_hash_indices)
    surface_face_types = [None]*len(surface_hash_indices)
    surface_face_element_idxs = [None]*len(surface_hash_indices)

    surface_elements = []
    surface_element_types = []
    surface_element_hashes = []
    surface_element_idxs = []
    for it, index in enumerate(surface_hash_indices):  # PARALLELIZE ME
        surface_faces[it] = element_faces[unique_face_indices[index]]
        surface_face_types[it] = element_types[unique_face_indices[index]]
        surface_face_element_idxs[it] = element_idxs[unique_face_indices[index]]

        # for the faces that define the surface also save the corresponding
        # elements and their hashes
        surface_elements.append(
            elements[unique_face_indices[index]])
        surface_element_types.append(
            element_types[unique_face_indices[index]])
        surface_element_hashes.append(
            element_hashes[unique_face_indices[index]])
        surface_element_idxs.append(
            element_idxs[unique_face_indices[index]])

    # find out, which element occurs how often
    _, unique_element_indices = np.unique(
        surface_element_hashes, return_index=True)

    # get the unique elements
    free_elements_unique = []
    free_element_types = []
    free_element_idxs = []
    for index in unique_element_indices:
        free_elements_unique.append(surface_elements[index])
        free_element_types.append(surface_element_types[index])
        free_element_idxs.append(surface_element_idxs[index])

        # sort by element types
    element_types = np.unique(surface_element_types)

    surface_elements = {}

    # sort the elements by type
    for element_type in element_types:

        free_elem = []
        free_idx = []

        element_locations = np.where(
            np.asarray(free_element_types) == element_type)[0]

        for loc in element_locations:
            free_elem.append(free_elements_unique[loc])
            free_idx.append(free_element_idxs[loc])

        surface_elements[element_type] = {
            'elements': np.asarray(free_elem),
            'element_idxs': np.asarray(free_idx),
        }

    return {
        'surface_faces': surface_faces,  # array
        'surface_face_types': surface_face_types,  # array
        'surface_face_element_idxs': surface_face_element_idxs,  # array
        'surface_elements': surface_elements  # dict with arrays, sorted by type
    }


def _dataset_triangulate_surface(surface_faces, element_types, element_idxs):
    """
    Generate tetraeders for the free faces.

    Args:
     free_faces (dict): The free (outward pointing) faces of the dataset.
      free_faces = {'free_faces': [ [face1], [face2], ...]}

    Returns:
     tets (array): The outward facing tetraeders.

    """
    triangles = []
    types = []
    idxs = []

    for it, face in enumerate(surface_faces):
        # just append a triangle
        if len(face) == 3:
            triangles.append(face)
            types.append(element_types[it])
            idxs.append(element_idxs[it])

        # a quad has to be split up into two triangles
        if len(face) == 4:

            # add two triangles and two ids and types
            triangles.append([face[0], face[1], face[2]])
            types.append(element_types[it])
            idxs.append(element_idxs[it])
            triangles.append([face[0], face[2], face[3]])
            types.append(element_types[it])
            idxs.append(element_idxs[it])

    return {
        'triangulation': triangles,
        'element_types': types,
        'element_idxs': idxs
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


def expand_integration_points_to_nodes(elemental_data, mesh_data):
    """
    Expand the data for the integration points to the nodes of an element.

    """
    pass
