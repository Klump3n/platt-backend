#!/usr/bin/env python3
"""
The class for a scene.

A scene contains a number of objects.

"""
import os
from backend.util.timestamp_to_sha1 import timestamp_to_sha1
from backend.scenes_object_prototype import _ObjectPrototype


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
        self._data_dir = data_dir  # This is already absolute

        # This turns a linux timestamp into a sha1 hash, to uniquely identify a
        # scene based on the time it was created.
        self._scene_name = timestamp_to_sha1()
        self._object_list = {}

    def add_object(
            self,
            object_path
    ):
        """
        Add one or multiple object(s) to the scene.

        There are two helper functions implemented in this method:

        * *verify_object_path*: Verify that the given object path contains
          simulation data that we can add. Do this by checking for a /fo or
          /frb subpath.
        * *add_one_object*: Add one object to the _object_list.

        Args:
         object_path (str, list (of str)): The relative path to the object
          root, relative to `data_dir`.

        Raises:
         TypeError: If ``type(object_path)`` is neither `os.PathLike` nor
          `list`.

        Todo:
         verify_object_path throws an exception that is probably not necessary.
         Assign a CRC32 hash to an object? Or CRC64?
         Only allow one object to be added at a time?

        """
        if (
                not isinstance(object_path, os.PathLike) and
                not isinstance(object_path, list)
        ):
            raise TypeError(
                'object_path is {}, expected either os.PathLike or list'.format(
                    type(object_path).__name__))

        # This joins two os.PathLike objects
        object_path = self._data_dir / object_path

        def verify_object_path(object_path):
            """
            Verify that the given object path contains simulation data that we
            can add.

            Do this by checking for a /fo or /frb subpath.

            Args:
             object_path (str, list (of str)): The relative path to the object
              root, relative to `data_dir`.

            Raises:
             ValueError: If `object_path` does not exist and/or `object_path`
              is not a directory.
             ValueError: If there is no 'fo' and/or 'frb' sub directory in
              `object_path.`

            Todo:
             The second exception is not really an exception..?? Make this
             return a boolean.

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

        def add_one_object(object_path):
            """
            Add one object to the _object_list.

            Args:
             object_path (str, list (of str)): The relative path to the object
              root, relative to `data_dir`.

            Returns:
             None: Nothing.

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

        Args:
         None: No parameters.

        Returns:
         str: The name (scene_hash) of the scene. This is created on
         initialization by creating a sha1 hash from the linux timestamp.

        """
        return self._scene_name

    def object_list(self):
        """
        Returns a list of all the objects in this scene.

        Create a sorted view (list) of the keys of the dict
        `self._object_list`. If this list is empty, append a notice to this
        list that there are no objects and return the list. Otherwise just
        return the (non empty) list.

        Returns:
         list: A list with objects in this scene or a notice, that there are
         no objects in this scene.

        """
        list_of_objects = sorted(self._object_list.keys())
        if len(list_of_objects) == 0:
            list_of_objects.append('This scene is empty.')

        return list_of_objects
