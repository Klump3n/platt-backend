#!/usr/bin/env python3
"""
Shape the parsed data, e.g. get the surface or free edges and so on. This is
intended as a module for the dataset parser.

"""
import numpy as np


def model_surface(nodes, elements):
    """
    Get the surface of a dataset.

    """
    bulk_edges_and_faces = _dataset_bulk_faces_and_edges(elements)

    bulk_faces = bulk_edges_and_faces['bulk_faces']
    free_faces = _dataset_free_faces(bulk_faces)

    tets = _dataset_free_tets(free_faces)

    bulk_edges = bulk_edges_and_faces['bulk_edges']
    wireframe_and_free_edges = _dataset_edges(bulk_edges)

    wireframe_lines = wireframe_and_free_edges['wireframe_lines']
    edge_lines = wireframe_and_free_edges['edge_lines']

    surface_nodes_and_map = _surface_nodes_and_map(nodes, free_faces)
    surface_node_map = surface_nodes_and_map['surface_node_map']

    remapped_nodes = surface_nodes_and_map['remapped_nodes']
    field_map = surface_nodes_and_map['field_map']

    remapped_tets_data = _remap_element_data(surface_node_map, tets)

    remapped_tets = {
        'type': 'tets',
        'points_per_unit': 3,
        'data': remapped_tets_data
    }

    nodes_center = _nodes_center(remapped_nodes)

    remapped_free_edges_data = _remap_element_data(
        surface_node_map, edge_lines)

    remapped_free_edges = {
        'type': 'free_edges',
        'points_per_unit': 2,
        'data': remapped_free_edges_data
    }

    remapped_wireframe_data = _remap_element_data(
        surface_node_map, wireframe_lines)

    remapped_wireframe = {
        'type': 'wireframe',
        'points_per_unit': 2,
        'data': remapped_wireframe_data
    }

    return {
        'field_map': field_map,
        'tets': remapped_tets,
        'node_count': len(surface_node_map),
        'nodes': remapped_nodes,
        'nodes_center': nodes_center,
        'free_edges': remapped_free_edges,
        'wireframe': remapped_wireframe
    }


def model_surface_fields(field_map, field_values):
    """
    Extract the surface field values.

    """
    remapped_field_data = _remap_index_data(field_map, field_values)

    remapped_field = {
        'type': 'field',
        'points_per_unit': 1,
        'data': remapped_field_data
    }

    return remapped_field


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


def _dataset_bulk_faces_and_edges(elements):
    """
    Returns the faces and edges and the hashes of those faces and edges for
    the bulk of the dataset.

    The returned data is sorted by the hash value.

    """
    fc = []
    faces = []
    faces_hashes = []

    eg = []
    edges = []
    edges_hashes = []

    # Iterate over all element types (c3d6, c3d8, ...) we find in elements
    for element_type in elements:

        # organization of faces for an element type
        element_data = elements[element_type]['data']  # data
        face_indices = elements[element_type]['fmt']['faces']
        edge_indices = elements[element_type]['fmt']['edges']

        # iteration over individual elements in the dataset
        for element in element_data:

            # for each face in the element append a hash of the sorted
            # element and the element to different lists
            for face in face_indices:
                element_face = []
                for corner in face:
                    element_face.append(element[corner])

                # faces.append(element_face)
                # faces_hashes.append(hash(tuple(sorted(element_face))))
                fc.append([hash(tuple(sorted(element_face))), element_face])

            for edge in edge_indices:
                line = sorted([element[edge[0]], element[edge[1]]])

                # edges.append(line)
                # edges_hashes.append(hash(tuple(line)))
                eg.append([hash(tuple(line)), line])

    fc = sorted(fc, key=lambda x: x[0])  # sort by first column
    eg = sorted(eg, key=lambda x: x[0])

    for face in fc:
        faces_hashes.append(face[0])
        faces.append(face[1])

    for edge in eg:
        edges_hashes.append(edge[0])
        edges.append(edge[1])

    return {
        'bulk_faces': {'faces': faces, 'faces_hashes': faces_hashes},
        'bulk_edges': {'edges': edges, 'edges_hashes': edges_hashes}
    }


def _dataset_free_faces(bulk_faces):
    """
    From all faces in the bulk select those who are on the surface.

    Works under the assumption that the faces_hashes are sorted.

    """
    faces = bulk_faces['faces']
    faces_hashes = bulk_faces['faces_hashes']

    # find out, which face occurs how often
    _, unique_indices, faces_hash_counts = np.unique(
        faces_hashes, return_counts=True, return_index=True)

    # we want the surfaces that occur only once
    surface_hash_indices = np.where(faces_hash_counts == 1)[0]

    # for the hashes that occur once we append the corresponding faces to
    # a list with all free faces. those faces are pointing outward
    free_faces = [None]*len(surface_hash_indices)
    for it, index in enumerate(surface_hash_indices):
        free_faces[it] = faces[unique_indices[index]]

    return {
        'free_faces': free_faces
    }


def _dataset_free_tets(free_faces):
    """
    Generate tetraeders for the free faces.

    """
    faces_data = free_faces['free_faces']

    tets = []

    for face in faces_data:
        if len(face) == 3:
            tets.append(face)
        if len(face) == 4:
            tets.append([face[0], face[1], face[2]])
            tets.append([face[0], face[2], face[3]])

    return tets


def _dataset_edges(bulk_edges):
    """
    For for edges in the dataset we build a wireframe and the datasets corner
    edges.

    """
    edges = bulk_edges['edges']
    edges_hashes = bulk_edges['edges_hashes']

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

    for it, index in enumerate(free_edges_hash_indices):
        free_edge = edges[unique_indices[index]]
        free_edges_lines[it] = free_edge

    for it, index in enumerate(wireframe_hash_indices):
        wireframe_edge = edges[unique_indices[index]]
        wireframe_edges[it] = wireframe_edge

    return {
        'edge_lines': free_edges_lines,
        'wireframe_lines': wireframe_edges
    }


def _surface_nodes_and_map(nodes, free_faces):
    """
    Return a map that points from the indices for the surface to new
    consecutive indices.

    """
    faces_data = free_faces['free_faces']

    # find a unique set of indices
    flat_faces = _flatten_nested_lists(faces_data)

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


def _remap_element_data(surface_node_map, data):
    """
    Reassign indices of some data based on the surface node map.

    This is to compress the data for transmission to the frontend.

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

    """
    remapped_data = []

    for index in field_map:
        remapped_data.append(data[index])

    return remapped_data


def _nodes_center(nodes_dict):
    """
    Return the center of the mesh.

    Assume that nodes is a list with length divisible by 3.

    """
    nodes = nodes_dict['data']
    x = nodes[0::3]
    y = nodes[1::3]
    z = nodes[2::3]

    return [np.mean(x), np.mean(y), np.mean(z)]
