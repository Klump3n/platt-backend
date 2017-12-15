#!/usr/bin/env python3
"""
Tests for the dataset_mangler.

"""
import unittest

import numpy as np
import pprint

import os
import sys
sys.path.append(os.path.join('..'))
import dataset_mangler as dm
import binary_formats


class Test_Mangler(unittest.TestCase):

    def setUp(self):
        # 27 element cubic mesh
        # an element i is defined by the corners
        # [i, i+1, i+17, i+16, i+4, i+5, i+21, i+20]
        self.cubic = {'c3d8': []}
        index_range = []
        front_cube_start_indices = [0, 1, 2, 4, 5, 6, 8, 9, 10]
        for index in [0, 16, 32]:
            for cube in front_cube_start_indices:
                index_range.append(cube + index)
        for i in index_range:
            self.cubic['c3d8'].append(
                [i, i+1, i+17, i+16, i+4, i+5, i+21, i+20]
            )

        # set the free faces
        self.free_faces = []

        front_faces_start_indices = [0, 1, 2, 4, 5, 6, 8, 9, 10]
        for i in front_faces_start_indices:
            self.free_faces.append([i, i+1, i+5, i+4])

        back_faces_start_indices = [63, 59, 55, 62, 58, 54, 61, 57, 53]
        for i in back_faces_start_indices:
            self.free_faces.append([i, i-4, i-5, i-1])

        left_faces_start_indices = [60, 56, 52, 44, 40, 36, 28, 24, 20]
        for i in left_faces_start_indices:
            self.free_faces.append([i, i-4, i-20, i-16])

        right_faces_start_indices = [3, 19, 35, 7, 23, 39, 11, 27, 43]
        for i in right_faces_start_indices:
            self.free_faces.append([i, i+16, i+20, i+4])

        bottom_faces_start_indices = [48, 49, 50, 32, 33, 34, 16, 17, 18]
        for i in bottom_faces_start_indices:
            self.free_faces.append([i, i+1, i-15, i-16])

        top_faces_start_indices = [15, 31, 47, 14, 30, 46, 13, 29, 45]
        for i in top_faces_start_indices:
            self.free_faces.append([i, i+16, i+15, i-1])

        # set the wireframe
        self.wf_edges = []
        self.model_edges = []

        for l in [
                front_faces_start_indices,
                back_faces_start_indices,
                left_faces_start_indices,
                right_faces_start_indices,
                bottom_faces_start_indices,
                top_faces_start_indices
        ]:
            # find the difference between the nodes
            dx = l[1] - l[0]
            dy = l[3] - l[0]

            for m in [0, 1, 2]:
                edge = [l[m], l[m]+dx]
                edge = [min(edge), max(edge)]
                self.model_edges.append(edge)
                self.wf_edges.append(edge)

            for m in [0, 3, 6]:
                edge = [l[m], l[m]+dy]
                edge = [min(edge), max(edge)]
                self.model_edges.append(edge)
                self.wf_edges.append(edge)

            for m in [1, 2, 4, 5, 7, 8]:
                edge = [l[m], l[m]+dy]
                edge = [min(edge), max(edge)]
                self.wf_edges.append(edge)

            for m in [3, 4, 5, 6, 7, 8]:
                edge = [l[m], l[m]+dx]
                edge = [min(edge), max(edge)]
                self.wf_edges.append(edge)

        # nodes -- this is R|^3 coordinates
        nodes = []
        for y in np.arange(4):
            for z in np.arange(4):
                for x in np.arange(4):
                    nodes.append([3.1*x, 1.3*y*y, 5.7*z])
        self.nodes = {'data': nodes}

        self.field = []
        for i in range(64):
            self.field.append(np.random.rand())

    def test__model_free_faces(self):
        """Get the free faces of the model

        """
        c3d8_data = {'c3d8': {'data': self.cubic['c3d8'], 'fmt': binary_formats.c3d8()}}
        res = dm._dataset_bulk_faces_and_edges(c3d8_data)
        bulk_faces = res['bulk_faces']
        res = dm._dataset_free_faces(bulk_faces)

        res_faces = res['free_faces']

        # permute result so that lowest index is first entry
        ordered_results = []
        for face in res_faces:
            min_val = min(face)
            faces = [[face[i - j] for i in range(len(face))] for j in range(len(face))]
            for cand in faces:
                if cand[0] == min_val:
                    ordered_results.append(cand)

        # permute result so that lowest index is first entry
        ordered_faces = []
        for face in self.free_faces:
            min_val = min(face)
            faces = [[face[i - j] for i in range(len(face))] for j in range(len(face))]
            for cand in faces:
                if cand[0] == min_val:
                    ordered_faces.append(cand)

        for face in ordered_results:
            self.assertIn(face, ordered_faces)

    def test__model_free_edges(self):
        """Get the free edges of the model

        """
        c3d8_data = {'c3d8': {'data': self.cubic['c3d8'], 'fmt': binary_formats.c3d8()}}
        res = dm._dataset_bulk_faces_and_edges(c3d8_data)
        bulk_edges = res['bulk_edges']
        res = dm._dataset_edges(bulk_edges)

        res_wf = res['wireframe_lines']
        res_fe = res['edge_lines']

        # sort edges
        ordered_wireframe = []
        for edge in res_wf:
            ordered_wireframe.append([min(edge), max(edge)])

        ordered_free_edges = []
        for edge in res_fe:
            ordered_free_edges.append([min(edge), max(edge)])

        for edge in ordered_free_edges:
            self.assertIn(edge, self.model_edges)

        for edge in ordered_wireframe:
            self.assertIn(edge, self.wf_edges)

    def test__surface_nodes_and_map(self):
        """Get a node map and a compressed set of nodes

        """
        c3d8_data = {'c3d8': {'data': self.cubic['c3d8'], 'fmt': binary_formats.c3d8()}}
        res = dm._dataset_bulk_faces_and_edges(c3d8_data)
        bulk_faces = res['bulk_faces']
        free_faces = dm._dataset_free_faces(bulk_faces)

        nodes = dm._surface_nodes_and_map(self.nodes, free_faces)
        self.assertTrue(False)
        # print(nodes)

    def test_model_surface(self):
        """Entry point for data mangling

        """
        c3d8_data = {'c3d8': {'data': self.cubic['c3d8'], 'fmt': binary_formats.c3d8()}}
        surf_res = dm.model_surface(self.nodes, c3d8_data)
        self.assertTrue(False)

    def test_model_surface_fields(self):
        """Get the field values

        """
        c3d8_data = {'c3d8': {'data': self.cubic['c3d8'], 'fmt': binary_formats.c3d8()}}
        surf_res = dm.model_surface(self.nodes, c3d8_data)
        node_map = surf_res['field_map']
        field_res = dm.model_surface_fields(node_map, self.field)
        self.assertTrue(False)

if __name__ == '__main__':
    unittest.main(verbosity=2)
