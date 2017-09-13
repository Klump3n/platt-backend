#!/usr/bin/env python3
"""
The class for a scene.

A scene contains a number of objects.

"""
import os
from backend.util.timestamp_to_sha1 import timestamp_to_sha1
from backend.scenes_dataset_prototype import _DatasetPrototype


class _ScenePrototype:
    """
    Contains a list of objects and methods for manipulating the scene.

    On initialization a unique identifier is generated and assigned to the
    scene.

    Args:
     data_dir (os.PathLike): A path pointing to the directory containing our
      simulation data.

    Raises:
     TypeError: If ``type(data_dir)`` is not `os.PathLike`.
     ValueError: If `data_dir` does not exist.

    Todo:
     Maybe it's worthwhile to declutter the add and delete functions by just
     allowing them to add one function.

    """

    def __init__(
            self,
            data_dir
    ):
        """
        Initialise an scene with some simulation data.

        """
        if not isinstance(data_dir, os.PathLike):
            raise TypeError('data_dir is {}, expected os.PathLike'.format(
                type(data_dir).__name__))

        if not data_dir.exists():
            raise ValueError('data_dir does not exist')

        self._data_dir = data_dir  # This is already absolute

        # This turns a linux timestamp into a sha1 hash, to uniquely identify a
        # scene based on the time it was created.
        self._scene_name = timestamp_to_sha1()

        self._dataset_list = {}

    def _add_one_dataset(self, dataset_path):
        """
        Add one dataset.

        Verify that the given object path contains simulation data that we
        can add. Do this by checking for a /fo or /frb subpath.

        Args:
         object_path (os.Pathlike): The path to the dataset we want to add

        Returns:
         dict: The metadata of the dataset we added.

        Raises:
         TypeError: If `dataset_path` is not `os.Pathlike`.
         ValueError: If `dataset_path` does not exist and/or `object_path`
          is not a directory.
         ValueError: If there is no 'fo' and/or 'frb' sub directory in
          `object_path.`

        """
        if not isinstance(dataset_path, os.PathLike):
            raise TypeError(
                'dataset_path is {}, expected os.PathLike'.format(
                    type(dataset_path).__name__))

        if not dataset_path.exists():
            raise ValueError('path \'{}\' does not exist'.format(
                dataset_path))

        if not dataset_path.is_dir():
            raise ValueError('dataset_path must point to a directory')

        # Casts this to os.pathlike
        fo_dir = dataset_path / 'fo'
        frb_dir = dataset_path / 'frb'

        # Raise an exception in case there are no subfolders called 'fo' or
        # 'frb'
        if not (fo_dir.exists() or frb_dir.exists()):
            raise ValueError(
                '{} contains neither \'fo\' nor \'frb\''.format(
                    dataset_path))

        # Create and append a new dataset
        new_dataset = _DatasetPrototype(dataset_path=dataset_path)
        dataset_meta = new_dataset.meta()
        dataset_hash = dataset_meta['datasetHash']
        self._dataset_list[dataset_hash] = new_dataset

        return dataset_meta

    def add_dataset(
            self,
            dataset_list
    ):
        """
        Add one or multiple object(s) to the scene.

        Args:
         dataset_list (list (of str)): The relative path to the object
          root, relative to `data_dir`.

        Raises:
         TypeError: If an entry in `dataset_list` is not `str`.
         TypeError: If ``type(dataset_list)`` is not `list`.
         ValueError: If ``len(dataset_list)`` is `0`.

        """
        if not isinstance(dataset_list, list):
            raise TypeError(
                'dataset_list is {}, expected list'.format(
                    type(dataset_list).__name__))

        if len(dataset_list) == 0:
            raise ValueError('dataset_list is empty')

        return_dict = {
            'href': '/scenes/{}'.format(self._scene_name),
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
                one_dataset_path = self._data_dir / one_dataset
                dataset_meta = self._add_one_dataset(one_dataset_path)
                return_dict['addDatasetsSuccess'].append(dataset_meta)

            # Catch everything that could have gone wrong and just report that
            # the dataset could not be added.
            except (TypeError, ValueError):
                try:
                    return_dict['addDatasetsFail'].append(one_dataset)
                except KeyError:
                    return_dict['addDatasetsFail'] = []
                    return_dict['addDatasetsFail'].append(one_dataset)

        if len(return_dict['addDatasetsSuccess']) == 0:
            # If we have nothing to return..
            return None
        else:
            return return_dict

    def delete_object(
            self,
            object_id
    ):
        """
        Remove one or multiple object(s) from the list of objects.

        Args:
         object_id (str, list (of str)): The relative path to the object
              root, relative to `data_dir`.

        Raises:
         TypeError: If ``type(object_path)`` is neither `os.PathLike` nor
          `list`.
         TypeError: If ``type(object_path)`` is `list` but the type of one
          list entry is not `os.PathLike`.

        Todo:
         See declutter todo in class.
        """

        if (not isinstance(object_id, os.PathLike) and
            not isinstance(object_id, list)):
            raise TypeError(
                'object_id is {}, expected either os.PathLike or list'.format(
                    type(object_id).__name__))

        if isinstance(object_id, str):
            # If we only have one object to remove...
            self._dataset_list.pop(object_id)

        else:
            # If we have a list of objects that we want to remove...
            for it, one_object_id in enumerate(object_id):

                # Check for type of the single object id in the list
                if not isinstance(one_object_id, os.PathLike):
                    raise TypeError(
                        'object_id[{}] is {}, expected os.PathLike'.format(
                            it, type(one_object_id).__name__))

                # Remove each object
                self._dataset_list.pop(one_object_id)

        return None

    def name(self):
        """
        Get the name for the scene.

        Args:
         None: No parameters.

        Returns:
         str: The name (scene_hash) of the scene. This is created on
         initialization by creating a sha1 hash from the linux timestamp.

        """
        return self._scene_name

    def dataset_list(self):
        """
        Returns a list of all the objects in this scene.

        Create a sorted view (list) of the keys of the dict
        `self._dataset_list`. If this list is empty, append a notice to this
        list that there are no objects and return the list. Otherwise just
        return the (non empty) list.

        Returns:
         list: A list with objects in this scene or a notice, that there are
         no objects in this scene.

        """
        list_of_objects = sorted(self._dataset_list.keys())
        if len(list_of_objects) == 0:
            list_of_objects.append('This scene is empty.')

        return list_of_objects
