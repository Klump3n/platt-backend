#!/usr/bin/env python3
"""
The class for a scene.

A scene contains a number of datasets.

"""
import os
import json
import logging
from backend.util.timestamp_to_sha1 import timestamp_to_sha1
from backend.scenes_dataset_prototype import _DatasetPrototype

from ws4py.messaging import TextMessage

# configure the ws4py logger
logger = logging.getLogger('ws4py')

from util.loggers import BackendLog as bl

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
            source_dict=None
    ):
        """
        Initialise an scene with some simulation data.

        """
        self.source = source_dict
        self.source_type = source_dict['source']

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

        # This turns a linux timestamp into a sha1 hash, to uniquely identify a
        # scene based on the time it was created.
        self._scene_hash = timestamp_to_sha1()

        self._dataset_list = {}

        self._colorbar_settings = {
            # selected can be either a hash, 'current' or 'values'
            'selected': None,
            'current': {'min': 0, 'max': 0},
            'values': {'min': -100, 'max': 100}
        }

        # an empty list for the websockets that connect to this scene
        self._websocket_list = []

        # keep track if we can patch stuff to the scene or not
        # if the scene is locked, we can't
        self._scene_locked = False

    def __del__(self):
        """
        Close all WebSockets when the class is no longer needed.

        """
        self.websocket_delete_scene()

    def name(self):
        """
        Get the name for the scene.

        Args:
         None: No parameters.

        Returns:
         str: The name (hash) of the scene.

        """
        return self._scene_hash

    def add_dataset(self, dataset_name):
        """
        Add one dataset.

        Verify that the given object path contains simulation data that we
        can add. Do this by checking for a /fo or /frb subpath.

        Args:
         dataset_name (str): Name of the dataset we want to add

        Returns:
         dict: The metadata of the dataset we added.

        Raises:
         TypeError: If `dataset_path` is not `os.Pathlike`.
         ValueError: If `dataset_path` does not exist.
         ValueError: If `dataset_path` is not a directory.
         ValueError: If there is no 'fo' and/or 'frb' sub directory in
          `dataset_path.`

        """
        # Create and append a new dataset
        # new_dataset = _DatasetPrototype(dataset_path=dataset_path)
        new_dataset = _DatasetPrototype(source_dict=self.source, dataset_name=dataset_name)
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
        except KeyError as e:
            bl.debug_warning('dataset_hash does not fit any dataset in scene: {}'.format(e))
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
        except KeyError as e:
            bl.debug_warning('dataset_hash does not fit any dataset in scene: {}'.format(e))
            raise ValueError('dataset_hash does not fit any dataset in scene')

    def colorbar_settings(self, colorbar_information=None):
        """
        Store colorbar information for the scene.

        """
        if colorbar_information:
            self._colorbar_settings = colorbar_information
            self.websocket_send(
                {
                    'update': 'colorbar'
                }
            )

        return self._colorbar_settings

    def is_scene_locked(self):
        """
        Returns True or False depending on the self._scene_locked var.

        """
        return self._scene_locked

    def lock_scene(self):
        """
        Sets self._scene_locked to True.

        """
        self._scene_locked = True

    def unlock_scene(self):
        """
        Sets self._scene_locked to False.

        """
        self._scene_locked = False

    def websocket_add(self, new_websocket):
        """
        Add a websocket to the scene.

        Args:
         new_websocket (ws4py.websocket.WebSocket): The WebSocket instance we
          want to add to the scene.

        """
        logger.info('Adding WebSocket to scene {}'.format(self._scene_hash))
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
        logger.info(
            'Removing WebSocket from scene {}'.format(self._scene_hash)
        )
        self._websocket_list.remove(old_websocket)
        return None

    def websocket_delete_scene(self):
        """
        Closes every WebSocket connection for this scene.

        """
        logger.info(
            'Closing every WebSocket for scene {}'.format(self._scene_hash)
        )
        for socket in self._websocket_list:
            socket.close()

        return None

    def websocket_send(self, message):
        """
        Send a message to all connected websockets.

        Args:
         message (JSON parsable object): Something we want to transmit to all
          the connected WebSocket instances. Must be parsable by json.dumps(),
          so strings, dicts, arrays and so on.

        """
        logger.info('Broadcasting message to scene {}'.format(self._scene_hash))
        msg = TextMessage(json.dumps(message))
        for socket in self._websocket_list:
            socket.send(msg.data, msg.is_binary)
        return None
