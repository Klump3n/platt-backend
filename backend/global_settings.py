#!/usr/bin/env python3
"""
A selection of globally available variables.

So far it only contains the scene_manager.

"""
from backend.scenes_manager import SceneManager

from util.loggers import BackendLog as bl

def init(source_dict=None):
    """
    Initialise the global variables.

    The scene_manager is an object that contains all the scenes on the server
    and exposes methods to manipulate them and the objects that are contained.

    Args:
     source_dict (dict): Information about the provided data source.

    Notes:
     Import this module everywhere you need to manipulate scenes.

    """
    bl.verbose("Creating global scene manager instance")
    global scene_manager        # This gets exposed
    scene_manager = SceneManager(source_dict=source_dict)
