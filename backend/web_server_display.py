"""
The web server class with all available RESTful api endpoints.

For example: call the server on SERVER_ADRESS/get_object_list to get a list
of the available objects in the data directory.
"""


# conda install cherrypy
import cherrypy

import backend.global_settings as global_settings
from backend.entry_pages import generate_entry_page


class ServerRoot:
    """
    Handle the data for fem-gl.
    """

    @cherrypy.expose
    def index(self):
        """
        The scene administration page.
        """

        return ('This page will at some point contain a command and control ' +
                'panel for our simulation data and scenes.')

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
    def default(self):
        """
        If we simply call HOST:PORT/scenes(/) we will get this message.
        """

        return 'No scene selected.'

    # Dismantle the URL
    def _cp_dispatch(self, vpath):
        """
        This looks at the url we call. If the first node is a valid scene_hash
        we generate an index.html file with this scene_hash encoded. Otherwise
        we generate an error message.
        """

        # If the first argument is a scene hash
        if vpath[0] in global_settings.global_scenes:

            # Pop the first argument from the stack
            cherrypy.request.params['scene_hash'] = vpath.pop(0)
            return self.ServerDisplayScene
        else:
            # Otherwise generate an error message
            return self.error

    @cherrypy.expose
    def error(self):
        """
        In case the scene does not exist.
        """

        return 'Sorry, this scene does not exist.'


class ServerDisplayScene:
    """
    This returns an individual index.html file with the scene_hash encoded
    into it.
    """

    @cherrypy.expose
    def default(self, scene_hash):

        # Return a prepared page
        return generate_entry_page(scene_hash)
