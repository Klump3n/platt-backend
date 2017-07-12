#!/usr/bin/env python3

import os
import time
import hashlib
from scenes_object_prototype import _ObjectPrototype


class _ScenePrototype:
    """
    Holds all the objects in a scene and also the meta data.
    """

    def __init__(
            self,
            data_dir=None
    ):
        """
        Initialise an empty scene.
        """

        if not isinstance(data_dir, os.PathLike):
            raise TypeError('data_dir is {}, expected os.PathLike'.format(
                type(data_dir).__name__))
        self._data_dir = data_dir  # This is already absolute

        # This turns a linux timestamp into a sha1 hash, to uniquely identify a
        # scene based on the time it was created.
        self._scene_name = hashlib.sha1(
            str(time.time()).encode('utf-8')).hexdigest()
        self._object_list = {}

        return None

    def add_object(
            self,
            object_path=None
    ):
        """
        Add one or multiple object(s) to the scene.

        object_path has to be either a string or a list of strings, the strings
        being the path to the object root.
        """

        if (not isinstance(object_path, os.PathLike) and
            not isinstance(object_path, list)):
            raise TypeError(
                'object_path is {}, expected either os.PathLike or list'.format(
                    type(object_path).__name__))

        # This joins two os.PathLike objects
        object_path = self._data_dir / object_path

        # Helper function for verifying the object path
        def verify_object_path(object_path):
            """
            Verify that the given object path contains simulation data that we
            can add.

            Do this by checking for a /fo or /frb subpath.
            """

            if not object_path.exists():
                raise ValueError('path \'{}\' does not exist'.format(
                    object_path))

            if not object_path.is_dir():
                raise ValueError('object_path must point to a directory')

            fo_dir = object_path / 'fo'
            frb_dir = object_path / 'frb'

            # Raise an exception in case there are no subfolders called 'fo' or
            # 'frb'
            if not (fo_dir.exists() or frb_dir.exists()):
                raise ValueError(
                    '{} neither contains \'fo\' nor \'frb\''.format(
                        object_path))

            return None

        # Helper function for adding one object to the scene
        def add_one_object(object_path):
            """
            Add one object to the _object_list.
            """

            new_object = _ObjectPrototype(
                object_path=object_path)
            object_name = new_object.name()

            if object_name not in self._object_list:
                self._object_list[object_name] = new_object
            else:
                print('{} is already in object_list'.format(object_name))

            return None

        # Verify the object path
        verify_object_path(object_path)

        # If we only have one object to add...
        if isinstance(object_path, os.PathLike):
            add_one_object(object_path=object_path)

        # If we have a list of objects that we want to add...
        else:
            for it, one_object_path in enumerate(object_path):

                # Check for type of the single object in the list
                if not isinstance(one_object_path, os.PathLike):
                    raise TypeError(
                        'object_path[{}] is {}, expected os.PathLike'.format(
                            it, type(one_object_path).__name__))

                # Add each object
                add_one_object(object_path=one_object_path)

        return None

    def delete_object(
            self,
            object_id=None
    ):
        """
        Remove one or multiple object(s) from the list of objects.

        object_id has to be either a string or a list of strings, the strings
        being the object ids.
        """

        if (not isinstance(object_id, os.PathLike) and
            not isinstance(object_id, list)):
            raise TypeError(
                'object_id is {}, expected either os.PathLike or list'.format(
                    type(object_id).__name__))

        if isinstance(object_id, str):
            # If we only have one object to remove...
            self._object_list.pop(object_id)

        else:
            # If we have a list of objects that we want to remove...
            for it, one_object_id in enumerate(object_id):

                # Check for type of the single object id in the list
                if not isinstance(one_object_id, os.PathLike):
                    raise TypeError(
                        'object_id[{}] is {}, expected os.PathLike'.format(
                            it, type(one_object_id).__name__))

                # Remove each object
                self._object_list.pop(one_object_id)

        return None

    def name(self):
        """
        Get the name for the scene.
        """

        return self._scene_name

