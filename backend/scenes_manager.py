#!/usr/bin/env python3

"""
This module takes care of storing and manipulating scenes.

"""
import os
import pathlib
from backend.scenes_scene_prototype import _ScenePrototype


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
    def __init__(self, data_dir):
        """
        Initialise the manager.

        If initialization `data_dir` is not of type `str` a TypeError will be
        raised. The `data_dir` is converted to a PathLike object.
        self._scene_list is a dictionary for containing scenes.

        """
        if not isinstance(data_dir, os.PathLike):
            raise TypeError('data_dir is {}, expected os.PathLike'.format(
                type(data_dir).__name__))

        # Check if the path exists
        if not data_dir.exists():
            raise ValueError(
                '{} does not exist'.format(data_dir.absolute()))

        # if not isinstance(data_dir, str):  # Yes, string.
        #     raise TypeError('data_dir is {}, expected str'.format(
        #         type(data_dir).__name__))

        # Set the data dir
        self._data_dir = data_dir.absolute()

        self._scene_list = {}

        return None

    def list_available_datasets(self):
    # def get_femdata_dirs(self):
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

        # Find all the folders in _data_dir
        dirs_in_data_dir = sorted(self._data_dir.glob('*/'))

        availableDatasets = {'availableDatasets': []}
        # data_folders = []

        for candidate in dirs_in_data_dir:
            if pathlib.Path(candidate / 'fo').is_dir():
                availableDatasets['availableDatasets'].append(
                    str(candidate.name))

        return availableDatasets

    # def scene_create(
    #         self,
    #         datasets
    # ):
    #     """
    #     Create a new scene with at least one object.

    #     This adds a ScenePrototype to `self._scene_list`.

    #     Args:
    #      object_path (list (of str)): A list of datasets we want to append to
    #       the scene.

    #     Returns:
    #      dict: A dict containing a link to the scene, a list of loaded datasets
    #      and potentially a list of datasets that for some reason could not be
    #      added.

    #     Raises:
    #      TypeError: If ``type(datasets)`` is not `list` and of it are not
    #       ``str``.

    #     Todo:
    #      Make it impossible to create an empty scene.

    #     """
    #     if not isinstance(datasets, list):
    #         raise TypeError('datasets is {}, expected list'.format(
    #             type(datasets).__name__))


    #     # Get a new instance of a scene
    #     new_scene = _ScenePrototype(data_dir=self._data_dir)
    #     scene_name = new_scene.name()

    #     # Cast each path to a os.Pathlike object and add the object to the scene
    #     for entry in datasets:

    #         if not isinstance(entry, str):
    #             raise TypeError('datasets entry is {}, expected str'.format(
    #                 type(entry).__name__))

    #         # Cast to pathlike object
    #         add_entry = pathlib.Path(entry)
    #         new_scene.add_object(object_path=add_entry)

    #     # # Append to scene with object to the list
    #     # self._scene_list[scene_name] = new_scene

    #     # # Return the name of the new scene so we keep our sanity.
    #     # return scene_name

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
        # Type checking for object path
        if not isinstance(dataset_list, list):
            raise TypeError('dataset_list is {}, expected list'.format(
                type(dataset_list).__name__))

        # Do nothing if the dataset list is empty
        if len(dataset_list) == 0:
            return None

        # # Get a new instance of a scene
        # new_scene = _ScenePrototype(data_dir=self._data_dir)
        # new_scene_hash = new_scene.name()
        # self._scene_list[new_scene_hash] = new_scene
        # return_dict = self.add_datasets(new_scene_hash, dataset_list)
        # return return_dict

        try:
            # Get a new instance of a scene
            new_scene = _ScenePrototype(data_dir=self._data_dir)
            new_scene_hash = new_scene.name()
            self._scene_list[new_scene_hash] = new_scene
            return_dict = self.add_datasets(new_scene_hash, dataset_list)
            return return_dict
        except (ValueError, TypeError):
            return None

        # if return_dict is not None:
        #     # Get the name and append it to the _scene_list
        #     scene_name = new_scene._name()
        #     self._scene_list[scene_name] = new_scene
        #     return return_dict
        # else:
        #     return None

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

        except ValueError:
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

    # def get_scene_infos(self):
    #     """
    #     Return a dict with all the scenes and information for every scene.

    #     Go through every key (= scene_hash) in self._scene_list and get the
    #     object information from the corresponding value (= _ScenePrototype
    #     object) by calling the internal method for retrieving the list of
    #     objects.

    #     The returned dict looks as follows:

    #     .. code-block:: python

    #      info_dict = {
    #          'scene_hash_1': {'object_list': 'obj_1', 'obj_3'},
    #          'scene_hash_2': {'object_list': 'obj_1', 'obj_2'},
    #          ...
    #      }

    #     Returns:
    #      dict: A dictionary containing all the scenes and all the objects in
    #      every scene.

    #     Todo:
    #      Rename to ``get_scenes_info``.

    #     """
    #     info_dict = {}

    #     for scene in self._scene_list:
    #         # Do this for every scene
    #         scene_info = {'object_list': self._scene_list[scene].object_list()}
    #         info_dict[scene] = scene_info

    #     return info_dict

    def delete_scene(self, scene_hash):
        """
        Delete a scene.

        Args:
         scene_hash (str): The scene_hash of the scene to be deleted.

        Returns:
         str, None: Returns the `scene_hash` that was deleted or None, if no
         scene could be found to be deleted.

        Raises:
         TypeError: If `scene_hash` is not of type `str`.

        """
        if not isinstance(scene_hash, str):
            raise TypeError('scene_hash is {}, expected str'.format(
                type(scene_hash).__name__))

        if scene_hash in self._scene_list:
            # Pop the whole _ScenePrototype object and return the deleted hash
            self._scene_list.pop(scene_hash)
            return scene_hash
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

                # Cast to os.PathLike
                one_dataset_path = target_scene._data_dir / one_dataset
                dataset_hash = target_scene.add_dataset(one_dataset_path)
                dataset_meta = target_scene._dataset_list[dataset_hash].meta()
                return_dict['addDatasetsSuccess'].append(dataset_meta)

            # Catch everything that could have gone wrong and just report that
            # the dataset could not be added. NOTE: This also catches the case
            # that an entry in the list was not a string, so we might run in to
            # trouble? But it came from a list, so it can also go back into a
            # list I guess... Maybe FIXME.
            except (TypeError, ValueError):
                try:
                    return_dict['addDatasetsFail'].append(one_dataset)
                except KeyError:
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
         dict: A dictionary containing all the loaded datasets meta information.

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
        except ValueError:
            # The dataset does not exist
            return None

        # If there are no more datasets left delete the scene
        if remaining_datasets == []:
            self.delete_scene(scene_hash)

        return remaining_datasets
