"""
The web server class with all available RESTful api endpoints.

For example: call the server on SERVER_ADRESS/get_object_list to get a list
of the available objects in the data directory.
"""

import cherrypy

import backend.global_settings as gloset
from backend.static.gen_index import make_index


class ServerRoot:
    """
    Handle the data for fem-gl.
    """

    @cherrypy.expose
    def index(self):
        """
        The scene administration page.
        """

        return (
            'This page will at some point contain a command and control ' +
            'panel for our simulation data and scenes.'
        )

class ServerScenesDispatcher:
    """
    Display scenes on the server.
    """

    def __init__(self):
        """
        Initialise the dispatcher.
        """

        self.ServerDisplayScene = ServerDisplayScene()

    @cherrypy.expose
    def index(self):
        """
        If we simply call HOST:PORT/scenes(/) we will get this message.
        """

        return make_index(
            scene_hash=None,
            with_menu=False, with_colorbar=False,
            overlay_message='No scene selected.'
        )

    def _cp_dispatch(self, vpath):
        """
        This looks at the url we call. If the first node is a valid scene_hash
        we generate an index.html file with this scene_hash encoded. Otherwise
        we generate an error message.
        """

        # If the first argument is a scene hash ...
        if vpath[0] in gloset.scene_manager.get_scene_infos():

            # ... pop the first argument from the stack,
            cherrypy.request.params['scene_hash'] = vpath.pop(0)
            return self.ServerDisplayScene

        # otherwise ...
        else:
            # ... generate an error message
            return self.error

    @cherrypy.expose
    def error(self):
        """
        In case the scene does not exist.
        """

        return make_index(
            scene_hash=None,
            with_menu=False, with_colorbar=False,
            overlay_message='Sorry, this scene does not exist.'
        )

class ServerDisplayScene:
    """
    This returns an individual index.html file with the scene_hash encoded
    into it.
    """

    @cherrypy.expose
    def default(self, scene_hash):

        # Return a prepared page
        return make_index(
            scene_hash=scene_hash,
            with_menu=True, with_colorbar=True,
            overlay_message=None
        )
