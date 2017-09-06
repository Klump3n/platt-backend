#!/usr/bin/env python3

"""
This module takes care of storing and manipulating scenes.

"""

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
    def __init__(
            self,
            data_dir=None
    ):
        """
        Initialise the manager.

        If initialization `data_dir` is not of type `str` a TypeError will be
        raised. The `data_dir` is converted to a PathLike object.
        self._scene_list is a dictionary for containing scenes.

        """

        if not isinstance(data_dir, str):  # Yes, string.
            raise TypeError('data_dir is {}, expected str'.format(
                type(data_dir).__name__))

        # Set the data dir
        self._data_dir = pathlib.Path(data_dir).absolute()

        self._scene_list = {}

        return None

    def get_femdata_dirs(self):
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

        data_folders = []

        for candidate in dirs_in_data_dir:
            if pathlib.Path(candidate / 'fo').is_dir():
                data_folders.append(str(candidate.name))

        return data_folders

    def get_scene_infos(self):
        """
        Return a dict with all the scenes and information for every scene.

        Go through every key (= scene_hash) in self._scene_list and get the
        object information from the corresponding value (= _ScenePrototype
        object) by calling the internal method for retrieving the list of
        objects.

        The returned dict looks as follows:

        .. code-block:: python

         info_dict = {
             'scene_hash_1': {'object_list': 'obj_1', 'obj_3'},
             'scene_hash_2': {'object_list': 'obj_1', 'obj_2'},
             ...
         }

        Returns:
         dict: A dictionary containing all the scenes and all the objects in
         every scene.

        Todo:
         Rename to ``get_scenes_info``.

        """
        info_dict = {}

        for scene in self._scene_list:
            # Do this for every scene
            scene_info = {'object_list': self._scene_list[scene].object_list()}
            info_dict[scene] = scene_info

        return info_dict

    def delete_scene(self, scene_id=None):
        """
        Delete a scene.

        If no `scene_id` is given, a message is printed.

        Args:
         scene_id (str, None): The scene_hash of the scene to be deleted.

        Returns:
         str, None: Returns the `scene_id` that was deleted or None, if no
         scene could be found to be deleted.

        Raises:
         TypeError: If `scene_id` is not of type `str`.

        Todo:
         Make this work with more than one scene.

        """

        if not isinstance(scene_id, str):
            raise TypeError('scene_id is {}, expected str'.format(
                type(scene_id).__name__))

        if scene_id in self._scene_list:
            self._scene_list.pop(scene_id)
            return scene_id

        else:
            print('No scene found to delete.')
            return None

    def new_scene(
            self,
            object_path=None
    ):
        """
        Create a new scene with an object.

        This adds a ScenePrototype to `self._scene_list`.

        Args:
         object_path (None, str, list (of str), defaults to None): The path to
          the objects we want to instantiate a new scene with.

        Returns:
         str: The name (scene_hash) of the newly created scene.

        Raises:
         TypeError: If ``type(object_path)`` is not `list` and/or entries
          thereof are not ``str``.

        Todo:
         Make it impossible to create an empty scene.

        """

        # Type checking for object path
        if not isinstance(object_path, list):  # Yes, string.
            raise TypeError('object_path is {}, expected list'.format(
                type(object_path).__name__))

        # Get a new instance of a scene
        new_scene = _ScenePrototype(data_dir=self._data_dir)
        scene_name = new_scene.name()

        # Cast each path to a os.Pathlike object and add the object to the scene
        for entry in object_path:

            # Type checking, if path is string
            if not isinstance(entry, str):  # Yes, string.
                raise TypeError('object_path entry is {}, expected str'.format(
                    type(entry).__name__))

            # Cast to pathlike object
            add_entry = pathlib.Path(entry)
            new_scene.add_object(object_path=add_entry)

        # Append to scene with object to the list
        self._scene_list[scene_name] = new_scene

        # Return the name of the new scene so we keep our sanity.
        return scene_name

    def scene(
            self,
            scene_id=None
    ):
        """
        Return a scene object.

        Args:
         scene_id (str or None, defaults to None): The unique identifier of
          the scene that we want to return.

        Returns:
         None or _ScenePrototype object: None if no scene with a matching id
         could be found, otherwise return the scene object.

        See Also:
         :py:class:`backend.scenes_scene_prototype._ScenePrototype`

        """

        try:
            # See which index fits to the provided scene id
            index = list(self._scene_list.keys()).index(scene_id)

            # Get all the scene objects out of the _scene_list
            scenes = list(self._scene_list.values())

            return scenes[index]

        except ValueError:
            return None


if __name__ == '__main__':
    # The use case would later be to load this file in global variables,
    # instantiating it once and then make that instance globally available.
    # In this case: make manager globally available.
    manager = SceneManager(data_dir='../example_data')
    name_a = manager.new_scene(object_path='object a_no_symlinks')
    name_b = manager.new_scene(object_path='object a_no_symlinks')
    manager.delete_scene('asd')
    print(manager.scene(name_b).name())
