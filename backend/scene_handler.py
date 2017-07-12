#!/usr/bin/env python3

"""
An instance for an empty scene.
"""

import pathlib
from scenes_scene_prototype import _ScenePrototype


class SceneManager:
    """
    Takes care of registering scenes.
    """

    def __init__(
            self,
            data_dir=None
    ):
        """
        Initialise the manager.

        E.g. set an empty scene list.
        """

        if not isinstance(data_dir, str):  # Yes, string.
            raise TypeError('data_dir is {}, expected str'.format(
                type(data_dir).__name__))

        # Set the data dir
        self._data_dir = pathlib.Path(data_dir).absolute()

        self._scene_list = {}

        return None

    def get_scene_list(self):
        """
        Return a dict with all the scenes in it.
        """
        return self._scene_list

    def delete_scene(self, scene_id=None):
        """
        Delete a scene.
        """

        if not isinstance(scene_id, str):
            raise TypeError('scene_id is {}, expected str'.format(
                type(scene_id).__name__))

        if scene_id in self._scene_list:
            self._scene_list.pop(scene_id)
        else:
            print('No scene found to delete.')

        return None

    def new_scene(
            self,
            object_path=None
    ):
        """
        Create a new scene with an object.
        """

        # Type checking for object path
        if not isinstance(object_path, str):  # Yes, string.
            raise TypeError('object_path is {}, expected str'.format(
                type(object_path).__name__))

        # Get a new instance of a scene
        new_scene = _ScenePrototype(data_dir=self._data_dir)
        scene_name = new_scene.name()

        # Cast the path to a os.Pathlike object and add the object to the scene
        object_path = pathlib.Path(object_path)
        new_scene.add_object(object_path=object_path)

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
        """


        # See which index fits to the provided scene id
        index = list(self._scene_list.keys()).index(scene_id)

        # Get all the scene objects out of the _scene_list
        scenes = list(self._scene_list.values())

        return scenes[index]

if __name__ == '__main__':
    # The use case would later be to load this file in global variables,
    # instantiating it once and then make that instance globally available.
    # In this case: make manager globally available.
    manager = SceneManager(data_dir='../example_data')
    name_a = manager.new_scene(object_path='object a_no_symlinks')
    name_b = manager.new_scene(object_path='object a_no_symlinks')

    print(manager.scene(name_b).name())
