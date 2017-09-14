#!/usr/bin/env python3
"""
The class for a scene.

A scene contains a number of datasets.

"""
import os
from backend.util.timestamp_to_sha1 import timestamp_to_sha1
from backend.scenes_dataset_prototype import _DatasetPrototype


class _ScenePrototype:
    """
    Contains a list of datasets and methods for manipulating the scene.

    On initialization a unique identifier is generated and assigned to the
    scene.

    When a dataset is added to a scene the unique identifier of the dataset is
    returned, otherwise None. Likewise for deleting a dataset.

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

    def name(self):
        """
        Get the name for the scene.

        Args:
         None: No parameters.

        Returns:
         str: The name (hash) of the scene.

        """
        return self._scene_name

    # def _add_one_dataset(self, dataset_path):
    #     """
    #     Add one dataset.

    #     Verify that the given object path contains simulation data that we
    #     can add. Do this by checking for a /fo or /frb subpath.

    #     Args:
    #      object_path (os.Pathlike): The path to the dataset we want to add

    #     Returns:
    #      dict: The metadata of the dataset we added.

    #     Raises:
    #      TypeError: If `dataset_path` is not `os.Pathlike`.
    #      ValueError: If `dataset_path` does not exist.
    #      ValueError: If `dataset_path` is not a directory.
    #      ValueError: If there is no 'fo' and/or 'frb' sub directory in
    #       `dataset_path.`

    #     """
    #     if not isinstance(dataset_path, os.PathLike):
    #         raise TypeError(
    #             'dataset_path is {}, expected os.PathLike'.format(
    #                 type(dataset_path).__name__))

    #     if not dataset_path.exists():
    #         raise ValueError('path \'{}\' does not exist'.format(
    #             dataset_path))

    #     if not dataset_path.is_dir():
    #         raise ValueError('dataset_path must point to a directory')

    #     # Casts this to os.pathlike
    #     fo_dir = dataset_path / 'fo'
    #     frb_dir = dataset_path / 'frb'

    #     # Raise an exception in case there are no subfolders called 'fo' or
    #     # 'frb'
    #     if not (fo_dir.exists() or frb_dir.exists()):
    #         raise ValueError(
    #             '{} contains neither \'fo\' nor \'frb\''.format(
    #                 dataset_path))

    #     # Create and append a new dataset
    #     new_dataset = _DatasetPrototype(dataset_path=dataset_path)
    #     dataset_meta = new_dataset.meta()
    #     dataset_hash = dataset_meta['datasetHash']
    #     self._dataset_list[dataset_hash] = new_dataset

    #     return dataset_meta

    # def add_datasets(
    #         self,
    #         dataset_list
    # ):
    #     """
    #     Add one or multiple dataset(s) to the scene.

    #     Args:
    #      dataset_list (list (of str)): The relative path to the object
    #       root, relative to `data_dir`.

    #     Raises:
    #      TypeError: If an entry in `dataset_list` is not `str`.
    #      TypeError: If ``type(dataset_list)`` is not `list`.
    #      ValueError: If ``len(dataset_list)`` is `0`.

    #     Notes:
    #      See FIXME in code.

    #     """
    #     if not isinstance(dataset_list, list):
    #         raise TypeError(
    #             'dataset_list is {}, expected list'.format(
    #                 type(dataset_list).__name__))

    #     if len(dataset_list) == 0:
    #         raise ValueError('dataset_list is empty')

    #     # Encode the scene hash into the return_dict
    #     return_dict = {
    #         'href': '/scenes/{}'.format(self._scene_name),
    #         'addDatasetsSuccess': []
    #     }

    #     # Add each object
    #     for one_dataset in dataset_list:
    #         try:
    #             if not isinstance(one_dataset, str):
    #                 raise TypeError(
    #                     'one_dataset is {}, expected str'.format(
    #                         type(one_dataset).__name__))

    #             # Cast to os.PathLike
    #             one_dataset_path = self._data_dir / one_dataset
    #             dataset_meta = self._add_one_dataset(one_dataset_path)
    #             return_dict['addDatasetsSuccess'].append(dataset_meta)

    #         # Catch everything that could have gone wrong and just report that
    #         # the dataset could not be added. NOTE: This also catches the case
    #         # that an entry in the list was not a string, so we might run in to
    #         # trouble? But it came from a list, so it can also go back into a
    #         # list I guess... Maybe FIXME.
    #         except (TypeError, ValueError):
    #             try:
    #                 return_dict['addDatasetsFail'].append(one_dataset)
    #             except KeyError:
    #                 return_dict['addDatasetsFail'] = []
    #                 return_dict['addDatasetsFail'].append(one_dataset)

    #     # If we have nothing to return..
    #     if len(return_dict['addDatasetsSuccess']) == 0:
    #         return None
    #     else:
    #         return return_dict

    def add_dataset(self, dataset_path):
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
         ValueError: If `dataset_path` does not exist.
         ValueError: If `dataset_path` is not a directory.
         ValueError: If there is no 'fo' and/or 'frb' sub directory in
          `dataset_path.`

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

        return dataset_hash

    def list_datasets(self):
        """
        Return a list of all the objects in this scene.

        Create a sorted view (list) of the keys of the dict
        `self._dataset_list`.

        Returns:
         list: A list with objects in this scene.

        """
        list_of_datasets = sorted(self._dataset_list.keys())
        return list_of_datasets

    def dataset(self, dataset_hash):
        """
        Return a dataset object for working with.

        Args:
         dataset_hash: The unique identifier for the dataset we want to access.

        Returns:
         _DatasetPrototype: The dataset that we want to access.

        Raises:
         TypeError: If ``type(dataset_hash)`` is not `str`.

        """
        if not isinstance(dataset_hash, str):
            raise TypeError('dataset_hash is {}, expected str'.format(
                type(dataset_hash).__name__))

        try:
            return self._dataset_list[dataset_hash]
        except KeyError:
            raise ValueError('dataset_hash does not fit any dataset in scene')

    def delete_dataset(self, dataset_hash):
        """
        Remove one dataset from the scene.

        Args:
         dataset_hash: The unique identifier for the dataset we want to delete.

        Returns:
         str: The hash of the dataset that was removed from the scene.

        Raises:
         TypeError: If ``type(dataset_hash)`` is not `str`.
         ValueError: If `dataset_hash` does not fit any dataset in the scene.

        """
        if not isinstance(dataset_hash, str):
            raise TypeError('dataset_hash is {}, expected str'.format(
                type(dataset_hash).__name__))

        try:
            self._dataset_list.pop(dataset_hash)
            return dataset_hash
        except KeyError:
            raise ValueError('dataset_hash does not fit any dataset in scene')

    # DELETING MULTIPLE DATASETS IS NOT NECESSARY BY DEFINITION OF THE API.
    # def delete_datasets(self, dataset_hash_list):
    #     """
    #     Remove one or multiple dataset(s) from the scene.

    #     Args:
    #      dataset_hash (list (of str)): A list of dataset hashes that shall be
    #       removed from the scene.

    #     Raises:
    #      TypeError: If ``type(dataset_hash)`` is neither `os.PathLike` nor
    #       `list`.
    #      TypeError: If ``type(object_path)`` is `list` but the type of one
    #       list entry is not `os.PathLike`.

    #     Todo:
    #      See declutter todo in class.

    #     """
    #     if not isinstance(dataset_hash_list, list):
    #         raise TypeError(
    #             'dataset_hash_list is {}, expected list'.format(
    #                 type(dataset_hash_list).__name__))


    #     # TODO: If the scene is going to be empty we have to remove the scene?
    #     # For this we would have to send a message......
    #     # Also: rework this shit...

    #     for dataset_hash in dataset_hash_list:
    #         result = self._delete_one_dataset(dataset_hash)

    #     return None
