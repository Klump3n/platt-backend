#!/usr/bin/env python3
"""
The class for a scene.

A scene contains a number of datasets.

"""
import os
import json
from backend.util.timestamp_to_sha1 import timestamp_to_sha1
from backend.scenes_dataset_prototype import _DatasetPrototype

from ws4py.messaging import TextMessage

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

        # an empty list for the websockets that connect to this scene
        self._websocket_list = []

    def name(self):
        """
        Get the name for the scene.

        Args:
         None: No parameters.

        Returns:
         str: The name (hash) of the scene.

        """
        return self._scene_name

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
            # Return the object
            return self._dataset_list[dataset_hash]
        except KeyError:
            raise ValueError('dataset_hash does not fit any dataset in scene')

    def delete_dataset(self, dataset_hash):
        """
        Remove one dataset from the scene.

        Args:
         dataset_hash: The unique identifier for the dataset we want to delete.

        Returns:
         list: The remaining datasets in the scene.

        Raises:
         TypeError: If ``type(dataset_hash)`` is not `str`.
         ValueError: If `dataset_hash` does not fit any dataset in the scene.

        """
        if not isinstance(dataset_hash, str):
            raise TypeError('dataset_hash is {}, expected str'.format(
                type(dataset_hash).__name__))

        try:
            self._dataset_list.pop(dataset_hash)

            # Delegate returning of the remainder to the standard method
            return self.list_datasets()
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

    def websocket_add(self, new_websocket):
        """
        Add a websocket to the scene.

        Args:
         new_websocket (ws4py.websocket.WebSocket): The WebSocket instance we
          want to add to the scene.

        """
        self._websocket_list.append(new_websocket)
        return None

    def websocket_remove(self, old_websocket):
        """
        Remove a websocket from the scene.

        This happens when a (web) client disconnects or closes the window.

        Args:
         old_websocket (ws4py.websocket.WebSocket): The WebSocket instance we
          want to remove from the scene.

        """
        self._websocket_list.remove(old_websocket)
        return None

    def websocket_send(self, message):
        """
        Send a message to all connected websockets.

        Args:
         message (JSON parsable object): Something we want to transmit to all
          the connected WebSocket instances. Must be parsable by json.dumps(),
          so strings, dicts, arrays and so on.

        """
        msg = TextMessage(json.dumps(message))
        for socket in self._websocket_list:
            socket.send(msg.data, msg.is_binary)
        return None
