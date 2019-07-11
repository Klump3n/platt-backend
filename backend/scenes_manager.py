#!/usr/bin/env python3
"""
This module takes care of storing and manipulating scenes.

"""
import os
import pathlib
import asyncio
import threading
from contextlib import suppress

from backend.scenes_scene_prototype import _ScenePrototype
import backend.interface_external_data as external_data

import backend.platt_proxy_client as platt_client

from util.loggers import BackendLog as bl

class SceneManager:
    """
    Stores scenes and contains methods for manipulating scenes.

    Some design notes:
    self._scene_list is a dictionary that contains scene objects (see
    :py:class:`backend.scenes_scene_prototype._ScenePrototype`). The dict will
    look as follows:

    .. code-block:: python

       self._scene_list = {
           'scene_hash_1': <_ScenePrototype object for scene_hash_1>,
           'scene_hash_2': <_ScenePrototype object for scene_hash_2>,
           ...
       }

    To now get any information about the scenes (except for the keys) you must
    use the methods contained in the _ScenePrototype objects.

    Args:
     data_dir (str): The (relative) path to some simulation data.

    Raises:
     TypeError: If `data_dir` is not of type `str`.

    """
    def __init__(self, source_dict=None):
        """
        Initialise the manager.

        If initialization `data_dir` is not of type `str` a TypeError will be
        raised. The `data_dir` is converted to a PathLike object.
        self._scene_list is a dictionary for containing scenes.

        """
        self.source = source_dict
        self.source_type = source_dict['source']

        self._scene_list = {}

        if self.source_type == 'local':
            data_dir = self.source['local']
            # Check if the path exists
            if not data_dir.exists():
                raise ValueError(
                    '{} does not exist'.format(data_dir.absolute()))

            # Set the data dir
            self._data_dir = data_dir.absolute()

        if self.source_type == 'external':
            self.ext_addr = source_dict['external']['addr']
            self.ext_port = source_dict['external']['port']

            connection_active_event = self.source["external"]["comm_dict"]["proxy_connection_active_event"]

            connection_active_event.wait()

            self._local_src_index = {}
            self._local_src_dataset_index = {}
            self._local_src_index = self.ext_src_index(update=True)

    def list_available_datasets(self):
        """
        Return a list with directories that contain simulation data in
        _data_dir.

        Check all the files we find in self.data_directory, check if it's a
        directory, if it's a directory check if there is a directory called
        'fo' in there. If that's the case we add it to the list we return
        in the end.

        Args:
         None: No parameters.

        Returns:
         list: A list containing the names of all the folders in _data_dir
         that potentially contain simulation data.

        Todo:
         Maybe put into objects module?
         Make this a bit more secure. Just checking for the 'fo' directory is a
         bit optimistic and could probably be exploited (then again: for
         what?).

        """
        if self.source_type == 'local':
            return self._list_available_datasets_local()
        if self.source_type == 'external':
            return self._list_available_datasets_external()
        else:
            return None

    def _list_available_datasets_local(self):
        """
        Returns locally available datasets.

        """
        # Find all the folders in _data_dir
        dirs_in_data_dir = sorted(self._data_dir.glob('*/'))

        availableDatasets = {'availableDatasets': []}
        # data_folders = []

        for candidate in dirs_in_data_dir:
            if pathlib.Path(candidate / 'fo').is_dir():
                availableDatasets['availableDatasets'].append(
                    str(candidate.name))

        return availableDatasets

    def _list_available_datasets_external(self):
        """
        Returns externally available datasets.

        """
        availableDatasets = {
            'availableDatasets': list(self._local_src_index.keys())}
        return availableDatasets

    def new_scene(self, dataset_list):
        """
        Create a new scene with an object.

        This adds a ScenePrototype to `self._scene_list`.

        Args:
         dataset_list (list (of str)): The path to the datasets we want to
          instantiate a new scene with.

        Returns:
         None, dict: `None` if no dataset could be added to a new scene and a
         dict with information what could be added and what not in the case
         that we could add dataset(s) to a new scene.

        Raises:
         TypeError: If ``type(object_path)`` is not `list`.

        Todo:
         Make it impossible to create an empty scene.

        """
        # Type checking for dataset_list
        if not isinstance(dataset_list, list):
            raise TypeError('dataset_list is {}, expected list'.format(
                type(dataset_list).__name__))

        # Do nothing if the dataset list is empty
        if len(dataset_list) == 0:
            return None

        # See which datasets are valid
        valid_datasets = []
        available_datasets = (
            self.list_available_datasets()['availableDatasets'])
        for dataset in dataset_list:
            if dataset in available_datasets:
                valid_datasets.append(dataset)

        # If there are no valid datasets to be added return None
        if len(valid_datasets) == 0:
            return None

        try:
            # Get a new instance of a scene
            new_scene = _ScenePrototype(source_dict=self.source)
            new_scene_hash = new_scene.name()
            self._scene_list[new_scene_hash] = new_scene
            # Here still dataset_list, so we can have a addDatasetFail entry
            return_dict = self.add_datasets(new_scene_hash, dataset_list)
            return return_dict
        except (ValueError, TypeError) as e:
            bl.debug_warning("Exception when creating new scene: {}".format(e))
            return None

    def scene(
            self,
            scene_hash
    ):
        """
        Return a scene object.

        Args:
         scene_hash (str): The unique identifier of the scene that we want to
          return.

        Returns:
         None or _ScenePrototype object: None if no scene with a matching hash
         could be found, otherwise return the scene object.

        Raises:
         TypeError: If ``type(scene_hash)`` is not `str`.

        See Also:
         :py:class:`backend.scenes_scene_prototype._ScenePrototype`

        """
        if not isinstance(scene_hash, str):
            raise TypeError('scene_hash is {}, expected str'.format(
                type(scene_hash).__name__))

        try:
            # See which index fits to the provided scene id
            index = list(self._scene_list.keys()).index(scene_hash)

            # Get all the scene objects out of the _scene_list
            scenes = list(self._scene_list.values())

            return scenes[index]

        except ValueError as e:
            bl.debug_warning("Scene with hash {} not found: {}".format(scene_hash, e))
            return None

    def list_scenes(self):
        """
        Return a dict containing the active scenes in the SceneManager.

        """
        return_dict = {
            'activeScenes': []
        }
        for active_scene in self._scene_list:
            return_dict['activeScenes'].append(active_scene)

        return return_dict

    def delete_scene(self, scene_hash):
        """
        Delete a scene.

        Args:
         scene_hash (str): The scene_hash of the scene to be deleted.

        Returns:
         dict, None: Returns the `scene_hash` that was deleted in a dict or
          None, if no scene could be found to be deleted.

        Raises:
         TypeError: If `scene_hash` is not of type `str`.

        """
        if not isinstance(scene_hash, str):
            raise TypeError('scene_hash is {}, expected str'.format(
                type(scene_hash).__name__))

        return_dict = {
            'sceneDeleted': '',
            'href': '/scenes'
        }

        if scene_hash in self._scene_list:
            # Pop the whole _ScenePrototype object and return the deleted hash
            self._scene_list.pop(scene_hash)
            return_dict['sceneDeleted'] = scene_hash
            return return_dict
        else:
            return None

    def add_datasets(self, scene_hash, dataset_list):
        """
        Add one or multiple dataset(s) to the scene.

        Args:
         scene_hash (str): The hash of the scene to which we want to add
          datasets.
         dataset_list (list (of str)): The relative path to the object
          root, relative to `data_dir`.

        Raises:
         TypeError: If ``type(scene_hash)`` is not `str`.
         TypeError: If an entry in `dataset_list` is not `str`.
         TypeError: If ``type(dataset_list)`` is not `list`.
         ValueError: If ``len(dataset_list)`` is `0`.

        Returns:
         None or dict: None if we could not add any datasets to the scene, or
         a dict if some or all datasets could be added.

        Notes:
         See FIXME in code.

        """
        if not isinstance(scene_hash, str):
            raise TypeError(
                'scene_hash is {}, expected str'.format(
                    type(scene_hash).__name__))

        target_scene = self.scene(scene_hash)

        if not isinstance(dataset_list, list):
            raise TypeError(
                'dataset_list is {}, expected list'.format(
                    type(dataset_list).__name__))

        if len(dataset_list) == 0:
            raise ValueError('dataset_list is empty')

        # Encode the scene hash into the return_dict
        return_dict = {
            'sceneHash': '{}'.format(scene_hash),
            'href': '/scenes/{}'.format(scene_hash),
            'addDatasetsSuccess': []
        }

        # Add each object
        for one_dataset in dataset_list:
            try:
                if not isinstance(one_dataset, str):
                    raise TypeError(
                        'one_dataset is {}, expected str'.format(
                            type(one_dataset).__name__))

                dataset_hash = target_scene.add_dataset(one_dataset)
                dataset_meta = target_scene._dataset_list[dataset_hash].meta()
                return_dict['addDatasetsSuccess'].append(dataset_meta)
                self.ext_src_dataset_index(update=True, dataset=one_dataset)

            # Catch everything that could have gone wrong and just report that
            # the dataset could not be added. NOTE: This also catches the case
            # that an entry in the list was not a string, so we might run in to
            # trouble? But it came from a list, so it can also go back into a
            # list I guess... Maybe FIXME.
            except (TypeError, ValueError) as e:
                bl.debug_warning("Exception when adding dataset {}: {}".format(one_dataset, e))
                try:
                    return_dict['addDatasetsFail'].append(one_dataset)
                except KeyError as f:
                    bl.debug_warning("Further exception: {}".format(e))
                    return_dict['addDatasetsFail'] = []
                    return_dict['addDatasetsFail'].append(one_dataset)

        # If we have nothing to return..
        if len(return_dict['addDatasetsSuccess']) == 0:
            return None
        else:
            return return_dict

    def list_loaded_datasets(self, scene_hash):
        """
        Return a list of datasets that are loaded in a scenes

        Args:
         scene_hash (str): The hash of the scene for which we want to list all
          loaded datasets.

        Returns:
         dict: A dictionary containing all the loaded datasets meta
         information.

        """
        if not isinstance(scene_hash, str):
            raise TypeError('scene_hash is {}, expected str'.format(
                    type(scene_hash).__name__))

        # If the scene does not exist
        if scene_hash not in self._scene_list:
            return None

        return_dict = {
            'loadedDatasets': []
        }

        target_scene = self.scene(scene_hash)

        for one_dataset in target_scene.list_datasets():
            # Get the meta data from each dataset in the target scene
            one_dataset_meta = target_scene.dataset(one_dataset).meta()
            return_dict['loadedDatasets'].append(one_dataset_meta)

        return return_dict

    def list_loaded_dataset_info(self, scene_hash, dataset_hash):
        """
        Return information about a dataset that is loaded into a scene.

        """
        if not isinstance(scene_hash, str):
            raise TypeError('scene_hash is {}, expected str'.format(
                    type(scene_hash).__name__))

        if not isinstance(dataset_hash, str):
            raise TypeError('dataset_hash is {}, expected str'.format(
                    type(dataset_hash).__name__))

        # If the scene does not exist
        if scene_hash not in self._scene_list:
            return None

        target_scene = self.scene(scene_hash)
        target_scene_datasets = target_scene.list_datasets()

        if dataset_hash not in target_scene_datasets:
            return None

        dataset_meta = target_scene.dataset(dataset_hash).meta()

        return dataset_meta

    def delete_loaded_dataset(self, scene_hash, dataset_hash):
        """
        Remove a dataset from a scene.

        If all datasets are gone the scene is to be deleted.

        Args:
         scene_hash (str): The hash of the scene from which we want to delete
          a dataset.
         dataset_hash (str): The hash of the dataset we want to delete.

        """
        if not isinstance(scene_hash, str):
            raise TypeError('scene_hash is {}, expected str'.format(
                    type(scene_hash).__name__))

        if not isinstance(dataset_hash, str):
            raise TypeError('dataset_hash is {}, expected str'.format(
                    type(dataset_hash).__name__))

        # If the scene does not exist
        if scene_hash not in self._scene_list:
            return None

        target_scene = self.scene(scene_hash)

        try:
            remaining_datasets = target_scene.delete_dataset(dataset_hash)
        except ValueError as e:
            bl.debug_warning("Exception in delete_loaded_dataset: {}".format(e))
            # The dataset does not exist
            return None

        # If there are no more datasets left delete the scene
        if remaining_datasets == []:
            self.delete_scene(scene_hash)

            # We should probably return something else so we can distinguish
            # between errors and deleted scenes.
            return None

        return_dict = {
            'datasetDeleted': dataset_hash,
            'href': '/scenes/{}'.format(scene_hash)
        }

        return return_dict

    def _target_dataset(self, scene_hash, dataset_hash):
        """
        Return a handle for a dataset in a scene.

        Args:
         scene_hash (str): The hash of the scene.
         dataset_hash (str): The hash of the dataset.

        Returns:
         _DatasetPrototype or None: The dataset or None if we could not find
         it.

        Raises:
         TypeError: If ``type(scene_hash)`` is not `str`.
         TypeError: If ``type(dataset_hash)`` is not `str`.

        """
        if not isinstance(scene_hash, str):
            raise TypeError('scene_hash is {}, expected str'.format(
                    type(scene_hash).__name__))

        if not isinstance(dataset_hash, str):
            raise TypeError('dataset_hash is {}, expected str'.format(
                    type(dataset_hash).__name__))

        # If the scene does not exist
        if scene_hash not in self._scene_list:
            return None

        target_scene = self.scene(scene_hash)

        target_scene_datasets = target_scene.list_datasets()

        if dataset_hash not in target_scene_datasets:
            return None

        dataset_handle = target_scene.dataset(dataset_hash)

        return dataset_handle

    def scene_colorbar_settings(self, scene_hash, colorbar_information=None):
        """
        GET or PATCH the colorbar settings for a scene.

        """
        # If the scene does not exist
        if scene_hash not in self._scene_list:
            return None

        target_scene = self.scene(scene_hash)

        new_colorbar_information = target_scene.colorbar_settings(
            colorbar_information)

        return new_colorbar_information

    def dataset_orientation(
            self, scene_hash, dataset_hash, set_orientation=None):
        """
        Get or patch (set) the orientation of a dataset.

        If data is None we assume we just want to GET some data, otherwise we
        want to update (PATCH) it.

        Args:
         scene_hash (str): The hash of the scene.
         dataset_hash (str): The hash of the dataset.
         set_orientation (None or list): None or some orientation data (16
          element list).

        Returns:
         dict or None: The dataset orientation or None if no orientation could
         be set.

        Raises:
         TypeError: If ``type(scene_hash)`` is not `str`.
         TypeError: If ``type(dataset_hash)`` is not `str`.

        Todos:
         Change the datasetOrientation dict to something less redundant.

        """
        if not isinstance(scene_hash, str):
            raise TypeError('scene_hash is {}, expected str'.format(
                    type(scene_hash).__name__))

        if not isinstance(dataset_hash, str):
            raise TypeError('dataset_hash is {}, expected str'.format(
                    type(dataset_hash).__name__))

        target_dataset = self._target_dataset(scene_hash, dataset_hash)

        # dataset or scene do not exist
        if target_dataset is None:
            return None

        dataset_meta = self.list_loaded_dataset_info(scene_hash, dataset_hash)
        dataset_orientation = target_dataset.orientation(set_orientation)

        return_dict = dataset_orientation
        return_dict['datasetMeta'] = dataset_meta

        if set_orientation is not None:
            target_scene = self.scene(scene_hash)
            target_scene.websocket_send(
                {
                    'datasetHash': dataset_hash,
                    'update': 'orientation'
                }
            )

        return return_dict

    def dataset_timesteps(self, scene_hash, dataset_hash, set_timestep=None):
        """
        GET or PATCH (set) the timestep(s) of a dataset.

        If data is None we assume we just want to GET some data, otherwise we
        want to update (PATCH) it.

        Args:
         scene_hash (str): The hash of the scene.
         dataset_hash (str): The hash of the dataset.
         set_timestep (None or str): None or a timestep (that refers to
          the list we can GET).

        Returns:
         dict: The dataset timestep(s).

        Raises:
         TypeError: If ``type(scene_hash)`` is not `str`.
         TypeError: If ``type(dataset_hash)`` is not `str`.
         TypeError: If ``type(set_timestep)`` is not `NoneType` or `str`.

        """
        if not isinstance(scene_hash, str):
            raise TypeError('scene_hash is {}, expected str'.format(
                    type(scene_hash).__name__))

        if not isinstance(dataset_hash, str):
            raise TypeError('dataset_hash is {}, expected str'.format(
                    type(dataset_hash).__name__))

        if set_timestep is not None:
            if not isinstance(set_timestep, str):
                raise TypeError('set_timestep is {}, expected None or str'.
                                format(type(set_timestep).__name__))

        target_dataset = self._target_dataset(scene_hash, dataset_hash)

        # dataset or scene do not exist
        if target_dataset is None:
            return None

        dataset_meta = self.list_loaded_dataset_info(scene_hash, dataset_hash)
        timestep_list = target_dataset.timestep_list()

        # Look if we want to select the previous or the next timestep
        if (
                set_timestep == '_prev_timestep' or
                set_timestep == '_next_timestep'
        ):
            current_timestep = target_dataset.timestep()
            current_timestep_index = timestep_list.index(current_timestep)

            if set_timestep == '_prev_timestep':
                new_timestep_index = current_timestep_index - 1
                if new_timestep_index < 0:
                    set_timestep = None
                else:
                    set_timestep = timestep_list[new_timestep_index]

            if set_timestep == '_next_timestep':
                new_timestep_index = current_timestep_index + 1
                if new_timestep_index > len(timestep_list) - 1:
                    set_timestep = None
                else:
                    set_timestep = timestep_list[new_timestep_index]

        selected_timestep = target_dataset.timestep(
            set_timestep)

        return_dict = {
            'datasetMeta': dataset_meta,
            'datasetTimestepList': timestep_list,
            'datasetTimestepSelected': selected_timestep,
        }

        if set_timestep is not None:
            target_scene = self.scene(scene_hash)
            websocket_payload = target_dataset.websocket_payload()
            target_scene.websocket_send(websocket_payload)

        return return_dict

    def dataset_fields(self, scene_hash, dataset_hash, set_field=None):
        """
        GET or PATCH (set) the field(s) of a dataset.

        If data is None we assume we just want to GET some data, otherwise we
        want to update (PATCH) it.

        Args:
         scene_hash (str): The hash of the scene.
         dataset_hash (str): The hash of the dataset.
         set_field (None or str): None or a field (that refers to
          the list we can GET).

        Returns:
         dict: The dataset field(s).

        Raises:
         TypeError: If ``type(scene_hash)`` is not `str`.
         TypeError: If ``type(dataset_hash)`` is not `str`.
         TypeError: If ``type(set_field)`` is not `NoneType` or `str`.

        """
        target_dataset = self._target_dataset(scene_hash, dataset_hash)

        # dataset or scene do not exist
        if target_dataset is None:
            return None

        dataset_meta = self.list_loaded_dataset_info(scene_hash, dataset_hash)

        field_dict = target_dataset.field_dict()
        selected_field = target_dataset.field(set_field)

        return_dict = {
            'datasetMeta': dataset_meta,
            'datasetFieldList': field_dict,
            'datasetFieldSelected': selected_field
        }

        if set_field is not None:
            # broadcast the changed field
            target_scene = self.scene(scene_hash)
            websocket_payload = target_dataset.websocket_payload()
            target_scene.websocket_send(websocket_payload)

        return return_dict

    def dataset_elementsets(self, scene_hash, dataset_hash,
                            set_elementset=None):
        """
        GET or PATCH (set) the elementset(s) of a dataset.

        If data is None we assume we just want to GET some data, otherwise we
        want to update (PATCH) it.

        Args:
         scene_hash (str): The hash of the scene.
         dataset_hash (str): The hash of the dataset.
         set_elementset (None or str): None or a elementset (that refers to
          the list we can GET).

        Returns:
         dict: The dataset elementset(s).

        Raises:
         TypeError: If ``type(scene_hash)`` is not `str`.
         TypeError: If ``type(dataset_hash)`` is not `str`.
         TypeError: If ``type(set_elementset)`` is not `NoneType` or `str`.

        """
        target_dataset = self._target_dataset(scene_hash, dataset_hash)

        # dataset or scene do not exist
        if target_dataset is None:
            return None

        dataset_meta = self.list_loaded_dataset_info(scene_hash, dataset_hash)

        elementset_dict = target_dataset.elementset_dict()
        selected_elementset = target_dataset.elementset(set_elementset)

        if selected_elementset == {}:
            selected_elementset = '__all__'

        return_dict = {
            'datasetMeta': dataset_meta,
            'datasetElementsetList': elementset_dict['elementsets'],
            'datasetElementsetSelected': selected_elementset
        }

        if set_elementset is not None:
            # broadcast the changed elementset
            target_scene = self.scene(scene_hash)
            websocket_payload = target_dataset.websocket_payload()
            target_scene.websocket_send(websocket_payload)

        return return_dict

    def dataset_tracking(self, scene_hash, dataset_hash, set_tracking=None):
        """
        GET or PATCH (set/toggle) the tracking of a dataset.

        """
        target_dataset = self._target_dataset(scene_hash, dataset_hash)

        # dataset or scene do not exist
        if target_dataset is None:
            return None

        dataset_meta = self.list_loaded_dataset_info(scene_hash, dataset_hash)

        return_dict = {
            'datasetMeta': dataset_meta,
            "datasetTrackingState": tracking
        }

        return return_dict

    def dataset_mesh_hash(self, scene_hash, dataset_hash):

        target_dataset = self._target_dataset(scene_hash, dataset_hash)

        # dataset or scene do not exist
        if target_dataset is None:
            return None

        dataset_meta = self.list_loaded_dataset_info(scene_hash, dataset_hash)

        surface_mesh = target_dataset.surface_mesh()  # here with argument?

        surface_mesh_hash = surface_mesh['mesh_hash']

        surface_field = target_dataset.surface_field()  # here with argument?

        surface_field_hash = surface_field['field_hash']

        return_dict = {
            'datasetMeta': dataset_meta,
            'datasetMeshHash': surface_mesh_hash,
            'datasetFieldHash': surface_field_hash
        }

        return return_dict

    def dataset_mesh_geometry(self, scene_hash, dataset_hash):
        """
        GET the currently displayable mesh of a dataset.

        Args:
         scene_hash (str): The hash of the scene.
         dataset_hash (str): The hash of the dataset.

        Returns:
         dict: The dataset mesh with surface_nodes, wireframe_indices,
         surface_indices and orientation.

        Raises:
         TypeError: If ``type(scene_hash)`` is not `str`.
         TypeError: If ``type(dataset_hash)`` is not `str`.

        """
        # if not isinstance(scene_hash, str):
        #     raise TypeError('scene_hash is {}, expected str'.format(
        #             type(scene_hash).__name__))

        # if not isinstance(dataset_hash, str):
        #     raise TypeError('dataset_hash is {}, expected str'.format(
        #             type(dataset_hash).__name__))

        target_dataset = self._target_dataset(scene_hash, dataset_hash)

        # dataset or scene do not exist
        if target_dataset is None:
            return None

        dataset_meta = self.list_loaded_dataset_info(scene_hash, dataset_hash)

        surface_mesh = target_dataset.surface_mesh()

        surface_mesh_hash = surface_mesh['mesh_hash']
        surface_nodes = surface_mesh['nodes']
        surface_tets = surface_mesh['tets']
        surface_nodes_center = surface_mesh['nodes_center']
        surface_wireframe = surface_mesh['wireframe']
        surface_free_edges = surface_mesh['free_edges']

        return_dict = {
            'datasetMeta': dataset_meta,
            'datasetMeshHash': surface_mesh_hash,
            'datasetSurfaceNodes': surface_nodes,
            'datasetSurfaceTets': surface_tets,
            'datasetSurfaceNodesCenter': surface_nodes_center,
            'datasetSurfaceWireframe': surface_wireframe,
            'datasetSurfaceFreeEdges': surface_free_edges,
        }

        return return_dict

    def dataset_mesh_field(self, scene_hash, dataset_hash):
        """
        GET the currently displayable mesh of a dataset.

        Args:
         scene_hash (str): The hash of the scene.
         dataset_hash (str): The hash of the dataset.

        Returns:
         dict: The dataset mesh with surface_nodes, wireframe_indices,
         surface_indices and orientation.

        Raises:
         TypeError: If ``type(scene_hash)`` is not `str`.
         TypeError: If ``type(dataset_hash)`` is not `str`.

        """
        if not isinstance(scene_hash, str):
            raise TypeError('scene_hash is {}, expected str'.format(
                    type(scene_hash).__name__))

        if not isinstance(dataset_hash, str):
            raise TypeError('dataset_hash is {}, expected str'.format(
                    type(dataset_hash).__name__))

        target_dataset = self._target_dataset(scene_hash, dataset_hash)

        # dataset or scene do not exist
        if target_dataset is None:
            return None

        dataset_meta = self.list_loaded_dataset_info(scene_hash, dataset_hash)

        selected_field = target_dataset.field()

        surface_field = target_dataset.surface_field()

        surface_field_hash = surface_field['field_hash']
        surface_field_values = surface_field['field']

        surface_field_min_max = target_dataset.surface_field_min_max()

        return_dict = {
            'datasetMeta': dataset_meta,
            'datasetFieldHash': surface_field_hash,
            'datasetFieldSelected': selected_field,
            'datasetSurfaceField': surface_field_values,
            'datasetSurfaceFieldExtrema': surface_field_min_max
        }

        return return_dict

    def ext_src_index(self, update=False):
        """
        Keep a copy of the index of the external source.

        Args:
         update (bool, defaults to False): If set to True it will query the
          proxy for an updated index, updates the local copy and then return
          that.

        """
        if update:

            ext_dict = external_data.index(
                source_dict=self.source, namespace=None)
            self._local_src_index = ext_dict

        return self._local_src_index

    def ext_src_dataset_index(self, update=False, dataset=None):
        """
        Keep a copy of the index for a dataset in the external source.

        Args:
         update (bool, defaults to False): If set to True it will query the
          proxy for an updated index, updates the local copy and then return
          that.

        """
        if not dataset:
            # Don't know what to return
            return

        return {dataset: self._local_src_index[dataset]}
