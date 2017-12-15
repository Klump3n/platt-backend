#!/usr/bin/env python3

"""
The api.
"""

import os
import re
import json

import hashlib
import time

import numpy as np

# conda install cherrypy
import cherrypy

import backend.data_backend as fem_mesh
import backend.global_settings as global_settings


# We only want to allow people to POST to it.
@cherrypy.tools.allow(methods=['POST'])
class ServerAPI:
    """
    Expose an API to control the server.
    """

    def __init__(self, data_directory):
        self.data_directory = data_directory

    @cherrypy.expose
    def connect_client(self):
        """
        Return a jsoned string with version number. Maybe more later?
        """
        # print('hey')
        return json.dumps({'program': 'calculix_clone',
                           'version': '1-alpha'})

    @cherrypy.expose
    def scenes_list(self):
        """
        Return a list of scenes.
        """
        return json.dumps(global_settings.global_scenes)

    @cherrypy.expose
    def scenes_create(self):
        """
        Create a new scene.
        """

        # Create a unique identifier for our scene -- ignoring that google
        # managed to create a collision of sha1 sums.
        identifier = hashlib.sha1(str(time.time()).encode('utf-8')).hexdigest()

        scene_prototype = {
            'metadata': {},
            'objects': {}
        }

        global_settings.global_scenes[identifier] = scene_prototype
        return json.dumps({'created': identifier})

    @cherrypy.expose
    @cherrypy.tools.json_in()
    def scenes_delete(self):
        """
        Delete a scene.
        """

        # Parse JSON
        json_input = cherrypy.request.json
        print(json_input)
        scene_hash = json_input['scene_hash']

        global_settings.global_scenes.pop(scene_hash)
        return json.dumps({'deleted': scene_hash})

    @cherrypy.expose
    def get_object_list(self):
        """
        Return a list of folders that potentially hold FEM data on
        catching 'get_object_list'

        Check all the files we find in self.data_directory, check if it's a
        directory, if it's a directory check if there is a directory called
        'fo' in there. If that's the case we add it to the list we return
        in the end.

        Returns a json file.
        """

        files_in_data_dir = os.listdir(self.data_directory)

        data_folders = []

        for file_name in files_in_data_dir:
            abs_file_path = os.path.join(self.data_directory, file_name)
            if os.path.isdir(abs_file_path):
                file_output_dir = os.path.join(abs_file_path, 'fo')
                if os.path.isdir(file_output_dir):
                    data_folders.append(file_name)

        return json.dumps({'data_folders': data_folders})

    @cherrypy.expose
    @cherrypy.tools.json_in()
    def get_object_properties(self):
        """
        Return a list of properties for a given element on catching
        'get_object_properties'

        Go through all timestep folders and look in every ef- and nf-folder
        for files. Append every file to an array, afterwards find the unique
        files in that array. Append this list to a list containing an entry
        for a simple wireframe (i.e. no field values, just the bare mesh).

        Returns a json file.
        """

        # Parse JSON
        json_input = cherrypy.request.json
        object_name = json_input['object_name']

        object_directory = os.path.join(self.data_directory, object_name, 'fo')

        # Get the smallest timestep.
        dirs_in_fo = os.listdir(object_directory)

        object_timesteps = []

        for timestep in dirs_in_fo:
            timestep_path = os.path.join(object_directory, timestep)
            if os.path.isdir(timestep_path):
                object_timesteps.append(timestep)
        object_timesteps = sorted(object_timesteps)

        initial_timestep = object_timesteps[0]

        # Get all available properties.
        file_array = []
        for path, _, files in os.walk(object_directory):
            if (os.path.basename(path) == 'no' or
                os.path.basename(path) == 'eo'):
            # if (os.path.basename(path) == 'nf' or
            #     os.path.basename(path) == 'ef'):
                for single_file in files:
                    if re.match(r'(.*)\.bin', single_file):
                        file_array.append(single_file)
        unique_field_names = np.unique(file_array)

        object_properties = ['wireframe']

        for field_name in unique_field_names:
            # Remove the .bin ending from the file.
            name_without_ending = re.match(r'(.*)\.bin', field_name).groups(0)[0]
            object_properties.append(name_without_ending)

        return json.dumps({'object_properties': object_properties,
                           'initial_timestep': initial_timestep})


    def get_sorted_timesteps(self, object_name):
        """
        Generate a sorted list of timesteps.

        Go through all the folders in the object/fo folder. Every folder
        here is a timestep.
        
        Returns a list of lists.
        """

        object_directory = os.path.join(self.data_directory, object_name, 'fo')

        object_timesteps = []
        sorted_timesteps = []

        dirs_in_fo = os.listdir(object_directory)

        for timestep in dirs_in_fo:
            timestep_path = os.path.join(object_directory, timestep)
            if os.path.isdir(timestep_path):
                object_timesteps.append([float(timestep), timestep])

        sorted_timesteps = sorted(object_timesteps)
        return sorted_timesteps

    @cherrypy.expose
    @cherrypy.tools.json_in()
    def get_object_timesteps(self):
        """
        Return a list of the available timesteps for a given element on
        catching 'get_object_timesteps'

        Go through all the folders in the object/fo folder. Every folder
        here is a timestep.

        Returns a json file.
        """

        json_input = cherrypy.request.json
        object_name = json_input['object_name']

        object_timesteps = self.get_sorted_timesteps(object_name)
        sorted_timesteps = []
        for timestep in object_timesteps:
            sorted_timesteps.append(timestep[1])
        return json.dumps({'object_timesteps': sorted_timesteps})

    @cherrypy.expose
    @cherrypy.tools.json_in()
    def get_timestep_before(self):
        """
        Given a timestep, find the previous timestep.

        Return the same timestep if there is no timestep before.
        """

        json_input = cherrypy.request.json
        object_name = json_input['object_name']
        current_timestep = json_input['current_timestep']

        object_timesteps = self.get_sorted_timesteps(object_name)
        sorted_timesteps = []
        for it in object_timesteps:
            sorted_timesteps.append(it[1])
        object_index = sorted_timesteps.index(current_timestep)
        if object_index == 0:
            return json.dumps({'previous_timestep': sorted_timesteps[0]})
        else:
            return json.dumps({'previous_timestep': sorted_timesteps[object_index - 1]})

    @cherrypy.expose
    @cherrypy.tools.json_in()
    def get_timestep_after(self):
        """
        Given a timestep, find the next timestep.

        Return the same timestep if there is no timestep after.
        """

        json_input = cherrypy.request.json
        object_name = json_input['object_name']
        current_timestep = json_input['current_timestep']

        object_timesteps = self.get_sorted_timesteps(object_name)
        sorted_timesteps = []
        for it in object_timesteps:
            sorted_timesteps.append(it[1])

        number_of_timesteps = len(sorted_timesteps)
        object_index = sorted_timesteps.index(current_timestep)
        if object_index == number_of_timesteps - 1:
            return json.dumps({'next_timestep': sorted_timesteps[number_of_timesteps - 1]})
        else:
            return json.dumps({'next_timestep': sorted_timesteps[object_index + 1]})

    @cherrypy.expose
    @cherrypy.tools.json_in()
    def mesher_init(self):
        """
        Load the mesher class.
        """

        json_input = cherrypy.request.json
        nodepath = json_input['nodepath']
        elementpath = json_input['elementpath']

        os.chdir(self.data_directory)
        self.mesh_index = fem_mesh.UnpackMesh(
            node_path=nodepath,
            element_path=elementpath
        )

        surface_nodes = self.mesh_index.return_unique_surface_nodes()
        surface_indexfile = self.mesh_index.return_surface_indices()
        surface_metadata = self.mesh_index.return_metadata()

        return json.dumps({'surface_nodes': surface_nodes,
                           'surface_indexfile': surface_indexfile,
                           'surface_metadata': surface_metadata.tolist()})

    @cherrypy.expose
    @cherrypy.tools.json_in()
    def get_timestep_data(self):
        """
        On getting a POST:get_some_data from the webserver we give
        the required data back.
        """

        json_input = cherrypy.request.json
        object_name = json_input['object_name']
        field = json_input['field']
        timestep = json_input['timestep']

        timestep_data = self.mesh_index.return_data_for_unique_nodes(object_name, field, timestep)

        output_data = []
        for datapoint in timestep_data:
            output_data.append(datapoint[0])

        return json.dumps({'timestep_data': output_data})

    @cherrypy.expose
    @cherrypy.tools.json_in()
    def requestTimestepData(self):
        """
        Deliver a JSON file to the caller containing an indexed list of
        surface triangles, surface node data, corresponding index data and
        also non-indexed wireframe data for the surface.
        """

        json_input = cherrypy.request.json
        meshName = json_input['meshName']
        timestep = json_input['timestep']

        pass

