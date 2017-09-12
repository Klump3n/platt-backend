#!/usr/bin/env python3
"""
This module contains the class for the API endpoints of the backend.

"""

import os
import re
import json

import numpy as np

# conda install cherrypy
import cherrypy

from util.version import version
import backend.data_backend as fem_mesh

# This imports the scene manager and the data_directory
import backend.global_settings as gloset


class ServerAPI:
    """
    This class contains the API endpoints of the backend.

    Any method that is exposed via `@cherrypy.expose` decorator can be reached
    under ``http://HOST:PORT/api/METHOD``, with ``METHOD`` being the exposed
    method.

    A new method with JSON (``http://HOST:PORT/api/a_new_method_with_json``)
    should be implemented as follows:

    .. code-block:: python

        @cherrypy.expose
        @cherrypy.tools.json_in()
        def a_new_method_with_json(self):

            input_json_dict = cherrypy.request.json
            incoming_value = input_json_dict['incoming_key']

            outgoing_value = some_function(incoming_value)
            output_dict = {'outgoing_key': outgoing_value}

            return json.dumps(outgoing_dict)

    The decorator `@cherrypy.expose` tells the class that we want this method
    to be reachable via the API. The decorator `@cherrypy.tools.json_in()`
    enables the method to receive a JSON file.
    We can read this JSON file into a dictionary and extract a value.
    We then create an outgoing dictionary and return this with json.dumps().

    We can of course omit the JSON decorator if we don't need to receive a
    JSON file.

    Notes:
     Any JSON package that should reach the API has to be delivered with a POST
     request.

    """

    @cherrypy.expose
    @cherrypy.tools.allow(methods=['GET'])
    @cherrypy.tools.json_out()
    def version(self):
        """
        Returns a dictionary containing the programs name and version, e.g.

        .. code-block:: python

         {
             "programName": "norderney",
             "programVersion": "alpha-1-gbfed333-dirty"
         }

        With this method a client can verify that the backend is running a
        compatible version.

        Args:
         None: Nothing.

        Returns:
         JSON dict: A dictionary containing program name and version.

        See Also:
         :py:meth:`client.util_client.test_host.target_online_and_compatible`

        """
        version_dict = version(detail='long')
        return json.dumps(version_dict)

    @cherrypy.expose
    @cherrypy.tools.allow(methods=['GET'])
    @cherrypy.tools.json_out()
    def datasets(self):
        """
        List the available fem simulation directories.

        A list of all available simulation data folders can be obtained from
        the scene_manager.

        Returns:
         JSON dict: A dictionary containing available `data_folders`.

        Todo:
         _dos is not part of the client module. Fix that!

        See Also:
         :py:meth:`backend.scenes_manager.SceneManager.get_femdata_dirs`
         :py:func:`_dos.do_objects.objects`

        """
        data_folders = gloset.scene_manager.get_femdata_dirs()
        return json.dumps({'availableDatasets': data_folders})

    @cherrypy.expose
    @cherrypy.tools.allow(methods=['GET', 'POST', 'DELETE', 'PATCH'])
    @cherrypy.tools.json_in()
    @cherrypy.tools.json_out()
    def scenes(
            self,
            scene_hash=None, dataset_hash=None, dataset_operation=None
    ):
        """
        Contains the logic for manipulating scenes over the API.

        Distributes the call parameters to subfunctions.

        """
        # Parse the HTTP method
        http_method = cherrypy.request.method

        ##################################################

        if (scene_hash is None and
            dataset_hash is None and
            dataset_operation is None
        ):
            # GET
            if http_method == 'GET':
                # There is nothing to parse
                output = self.get_scenes()

            # POST
            if http_method == 'POST':

                # Parse datasetsToAdd from JSON
                try:
                    json_input = cherrypy.request.json
                    datasets = json_input['datasetsToAdd']
                    output = self.post_scenes(datasets)

                except ValueError as e:
                    print('{}'.format(e))
                    output = None

        ##################################################

        if (scene_hash is not None and
            dataset_hash is None and
            dataset_operation is None
        ):
            # GET
            if http_method == 'GET':
                pass

            # POST
            if http_method == 'POST':
                pass

            # DELETE
            if http_method == 'DELETE':
                pass

        ##################################################

        if (scene_hash is not None and
            dataset_hash is not None and
            dataset_operation is None
        ):
            # GET
            if http_method == 'GET':
                pass

            # DELETE
            if http_method == 'DELETE':
                pass

        ##################################################

        if (scene_hash is not None and
            dataset_hash is not None and
            dataset_operation is not None
        ):
            # GET
            if http_method == 'GET':
                pass

            # PATCH
            if http_method == 'PATCH':
                pass

        ##################################################

        # Return valid JSON
        return json.dumps(output)

    def get_scenes(self):
        """
        Return a list of scenes.

        A list of created scenes can be obtained from the scene_manager.

        Returns:
         dict: A dictionary containing a scenes and the objects within
         each scene.

        See Also:
         :py:meth:`backend.scenes_manager.SceneManager.get_scene_infos`
         :py:func:`_dos.do_scenes.scenes_list`

        """
        scenes = gloset.scene_manager.get_scene_infos()
        return scenes

    def post_scenes(self, datasets):
        """
        Create a new scene.

        We expect a JSON package with key 'object_path'. The value has to be a
        list, containing valid objects. If the list is empty, an empty scene
        will be created.

        Args:
         datasets (list): A list of datasets that are to be appended to the
          new scene.

        Returns:
         dict: A dictionary containing a the unique hash of the scene,
         that has been created.

        See Also:
         :py:meth:`backend.scenes_manager.SceneManager.new_scene`
         :py:func:`_dos.do_scenes.scenes_create`

        """
        scene_id = gloset.scene_manager.new_scene(object_path=object_path)
        return {'created': scene_id}

    # @cherrypy.expose
    # def scenes_infos(self):
    #     """
    #     Return a list of scenes.

    #     A list of created scenes can be obtained from the scene_manager.

    #     Returns:
    #      JSON dict: A dictionary containing a scenes and the objects within
    #      each scene.

    #     See Also:
    #      :py:meth:`backend.scenes_manager.SceneManager.get_scene_infos`
    #      :py:func:`_dos.do_scenes.scenes_list`

    #     """
    #     scenes = gloset.scene_manager.get_scene_infos()
    #     return json.dumps(scenes)

    @cherrypy.expose
    @cherrypy.tools.json_in()
    def scenes_create(self):
        """
        Create a new scene.

        We expect a JSON package with key 'object_path'. The value has to be a
        list, containing valid objects. If the list is empty, an empty scene
        will be created.

        Expected JSON package:
         ``{'object_path': ['list', 'with', 'objects']}``

        Returns:
         JSON dict: A dictionary containing a the unique hash of the scene,
         that has been created.

        See Also:
         :py:meth:`backend.scenes_manager.SceneManager.new_scene`
         :py:func:`_dos.do_scenes.scenes_create`

        """
        json_input = cherrypy.request.json
        object_path = json_input['object_path']

        scene_id = gloset.scene_manager.new_scene(object_path=object_path)
        return json.dumps(
            {'created': scene_id}
        )

    @cherrypy.expose
    @cherrypy.tools.json_in()
    def scenes_delete(self):
        """
        Delete a scene.

        """
        # Parse JSON
        json_input = cherrypy.request.json
        # print(json_input)
        scene_hash = json_input['scene_hash']

        deleted_scene_hash = gloset.scene_manager.delete_scene(scene_hash)

        return json.dumps({'deleted': deleted_scene_hash})

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

