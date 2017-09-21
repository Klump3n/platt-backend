#!/usr/bin/env python3
"""
A selection of globally available variables.

So far it only contains the scene_manager.

"""
import os
from backend.scenes_manager import SceneManager


def init(data_dir):
    """
    Initialise the global variables.

    The scene_manager is an object that contains all the scenes on the server
    and exposes methods to manipulate them and the objects that are contained.

    Args:
     data_dir (os.PathLike): The directory that contains the simulation data.

    Notes:
     Import this module everywhere you need to manipulate scenes.

    """
    global scene_manager        # This gets exposed
    scene_manager = SceneManager(data_dir)
