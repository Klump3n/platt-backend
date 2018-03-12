#!/usr/bin/env python3
"""
This module contains the class for the API endpoints of the backend.

"""
import json

# conda install cherrypy
import cherrypy

import util.version

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
        version_dict = util.version.version(detail='long')
        # return json.dumps(version_dict)
        return version_dict

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
        available_datasets_dict = (
            gloset.scene_manager.list_available_datasets())
        # return json.dumps(available_datasets_dict)
        return available_datasets_dict

    @cherrypy.expose
    @cherrypy.tools.allow(methods=['GET', 'POST', 'DELETE', 'PATCH'])
    @cherrypy.tools.json_in()
    @cherrypy.tools.json_out()
    def scenes(
            self,
            scene_hash=None, dataset_hash=None,
            dataset_operation=None, mesh_operation=None
    ):
        """
        Contains the logic for manipulating scenes over the API.

        Distributes the call parameters to subfunctions.

        """
        # Parse the HTTP method
        http_method = cherrypy.request.method

        # Init the output
        output = None

        ##################################################

        if (
                scene_hash is None and
                dataset_hash is None and
                dataset_operation is None and
                mesh_operation is None
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

                except (KeyError, TypeError) as e:
                    print('{}'.format(e))
                    output = None

        ##################################################

        if (
                scene_hash is not None and
                dataset_hash is None and
                dataset_operation is None and
                mesh_operation is None
        ):
            # GET
            if http_method == 'GET':
                output = self.get_scenes_scenehash(scene_hash)

            # POST
            if http_method == 'POST':
                # Parse datasetsToAdd from JSON
                try:
                    json_input = cherrypy.request.json
                    datasets = json_input['datasetsToAdd']
                    output = self.post_scenes_scenehash(scene_hash, datasets)

                except (KeyError, TypeError) as e:
                    print('{}'.format(e))
                    output = None

            # DELETE
            if http_method == 'DELETE':
                output = self.delete_scenes_scenehash(scene_hash)

        ##################################################

        if (
                scene_hash is not None and
                dataset_hash is not None and
                dataset_operation is None and
                mesh_operation is None
        ):
            # GET
            if http_method == 'GET':
                output = self.get_dataset_scenes_scenehash_datasethash(
                    scene_hash, dataset_hash)

            # DELETE
            if http_method == 'DELETE':
                output = self.delete_dataset_scenes_scenehash_datasethash(
                    scene_hash, dataset_hash)

        ##################################################

        if (
                scene_hash is not None and
                dataset_hash is not None and
                dataset_operation is not None and
                mesh_operation is None
        ):

            # GET
            if http_method == 'GET':

                if dataset_operation == 'orientation':
                    output = self.get_scenes_scenehash_datasethash_orientation(
                        scene_hash, dataset_hash)

                ##################################################

                if dataset_operation == 'timesteps':
                    output = self.get_scenes_scenehash_datasethash_timesteps(
                        scene_hash, dataset_hash)

                ##################################################

                if dataset_operation == 'fields':
                    output = self.get_scenes_scenehash_datasethash_fields(
                        scene_hash, dataset_hash)

                ##################################################

                if dataset_operation == 'mesh':
                    output = self.get_scenes_scenehash_datasethash_mesh(
                        scene_hash, dataset_hash)

            # PATCH
            if http_method == 'PATCH':

                if dataset_operation == 'orientation':

                    # Parse datasetsToAdd from JSON
                    try:
                        json_input = cherrypy.request.json
                        orientation = json_input['datasetOrientation']
                        output = (
                            self.
                            patch_scenes_scenehash_datasethash_orientation(
                                scene_hash, dataset_hash,
                                new_orientation=orientation)
                        )

                    except (KeyError, TypeError) as e:
                        print('{}'.format(e))
                        output = None

                ##################################################

                if dataset_operation == 'timesteps':

                    # Parse datasetsToAdd from JSON
                    try:
                        json_input = cherrypy.request.json
                        timestep = json_input['datasetTimestepSelected']
                        output = (
                            self.patch_scenes_scenehash_datasethash_timesteps(
                                scene_hash, dataset_hash,
                                new_timestep=timestep)
                        )

                    except (KeyError, TypeError) as e:
                        print('{}'.format(e))
                        output = None

                ##################################################

                if dataset_operation == 'fields':

                                        # Parse datasetsToAdd from JSON
                    try:
                        json_input = cherrypy.request.json
                        field = json_input['datasetFieldSelected']
                        output = (
                            self.patch_scenes_scenehash_datasethash_fields(
                                scene_hash, dataset_hash,
                                new_field=field)
                        )

                    except (KeyError, TypeError) as e:
                        print('{}'.format(e))
                        output = None

        ##################################################

        if (
                scene_hash is not None and
                dataset_hash is not None and
                dataset_operation is not None and
                mesh_operation is not None
        ):
            # GET
            if http_method == 'GET':

                if dataset_operation == 'mesh':

                    if mesh_operation == 'hash':
                        output = self.get_scenes_scenehash_datasethash_mesh_hash(
                            scene_hash, dataset_hash)

                    if mesh_operation == 'geometry':
                        output = self.get_scenes_scenehash_datasethash_mesh_geometry(
                            scene_hash, dataset_hash)

                    if mesh_operation == 'field':
                        output = self.get_scenes_scenehash_datasethash_mesh_field(
                            scene_hash, dataset_hash)


        ##################################################

        # Return valid JSON
        # json.dumps(None) = null
        # return json.dumps(output)
        return output

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
        # scenes = gloset.scene_manager.get_scene_infos()
        scenes = gloset.scene_manager.list_scenes()
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
        new_scene = gloset.scene_manager.new_scene(datasets)
        return new_scene

    def get_scenes_scenehash(self, scene_hash):
        """
        Get information about a scene.

        """
        loaded_datasets = gloset.scene_manager.list_loaded_datasets(scene_hash)
        return loaded_datasets

    def post_scenes_scenehash(self, scene_hash, datasets):
        """
        Add datasets to a scene.

        """
        added_datasets = gloset.scene_manager.add_datasets(
            scene_hash, datasets)
        return added_datasets

    def delete_scenes_scenehash(self, scene_hash):
        """
        Delete a scene.

        """
        deleted_scene = gloset.scene_manager.delete_scene(scene_hash)
        return deleted_scene

    def get_dataset_scenes_scenehash_datasethash(
            self, scene_hash, dataset_hash):
        """
        Get information about a dataset.

        """
        dataset_information = gloset.scene_manager.list_loaded_dataset_info(
            scene_hash, dataset_hash)
        return dataset_information

    def delete_dataset_scenes_scenehash_datasethash(
            self, scene_hash, dataset_hash):
        """
        Delete a dataset from a scene.

        """
        deleted_dataset = gloset.scene_manager.delete_loaded_dataset(
            scene_hash, dataset_hash)
        return deleted_dataset

    def get_scenes_scenehash_datasethash_orientation(
            self, scene_hash, dataset_hash):
        """
        Get the orientation of a dataset.

        """
        dataset_orientation = gloset.scene_manager.dataset_orientation(
            scene_hash, dataset_hash)
        return dataset_orientation

    def patch_scenes_scenehash_datasethash_orientation(
            self, scene_hash, dataset_hash, new_orientation):
        """
        Set the orientation of a dataset.

        """
        dataset_orientation = gloset.scene_manager.dataset_orientation(
            scene_hash, dataset_hash, set_orientation=new_orientation)
        return dataset_orientation

    def get_scenes_scenehash_datasethash_timesteps(
            self, scene_hash, dataset_hash):
        """
        Get the timesteps of a dataset.

        """
        dataset_timesteps = gloset.scene_manager.dataset_timesteps(
            scene_hash, dataset_hash)
        return dataset_timesteps

    def patch_scenes_scenehash_datasethash_timesteps(
            self, scene_hash, dataset_hash, new_timestep):
        """
        Set the timestep of a dataset.

        """
        dataset_timesteps = gloset.scene_manager.dataset_timesteps(
            scene_hash, dataset_hash, set_timestep=new_timestep)
        return dataset_timesteps

    def get_scenes_scenehash_datasethash_fields(
            self, scene_hash, dataset_hash):
        """
        Get the fields of a dataset.

        """
        dataset_fields = gloset.scene_manager.dataset_fields(
            scene_hash, dataset_hash)
        return dataset_fields

    def patch_scenes_scenehash_datasethash_fields(
            self, scene_hash, dataset_hash, new_field):
        """
        Set the field of a dataset.

        """
        dataset_fields = gloset.scene_manager.dataset_fields(
            scene_hash, dataset_hash, set_field=new_field)
        return dataset_fields

    def get_scenes_scenehash_datasethash_mesh(
            self, scene_hash, dataset_hash):
        """
        Get the mesh (hash, geometry and field) data of a dataset.

        """
        dataset_mesh = gloset.scene_manager.dataset_mesh(
            scene_hash, dataset_hash)

        return dataset_mesh

    def get_scenes_scenehash_datasethash_mesh_hash(
            self, scene_hash, dataset_hash):
        """
        Get the hashes of the mesh data of a dataset.

        """
        dataset_mesh_hash = gloset.scene_manager.dataset_mesh_hash(
            scene_hash, dataset_hash)

        return dataset_mesh_hash

    def get_scenes_scenehash_datasethash_mesh_geometry(
            self, scene_hash, dataset_hash):
        """
        Get the geometry data of a dataset.

        """
        dataset_mesh_geometry = gloset.scene_manager.dataset_mesh_geometry(
            scene_hash, dataset_hash)

        return dataset_mesh_geometry

    def get_scenes_scenehash_datasethash_mesh_field(
            self, scene_hash, dataset_hash):
        """
        Get the field data of a dataset.

        """
        dataset_mesh_field = gloset.scene_manager.dataset_mesh_field(
            scene_hash, dataset_hash)

        return dataset_mesh_field
