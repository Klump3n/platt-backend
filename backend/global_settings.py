#!/usr/bin/env python3

"""
A list of globally available variables.
"""

from backend.scenes_manager import SceneManager


def init(data_dir):
    """
    Initialise the global variables.
    """

    # An object that contains all the scenes on the server and exposes methods
    # to manipulate them and the objects that are contained.
    global scene_manager
    scene_manager = SceneManager(data_dir=data_dir)
