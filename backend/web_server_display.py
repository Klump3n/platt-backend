"""
The web server class with all available RESTful api endpoints.

For example: call the server on SERVER_ADRESS/get_object_list to get a list
of the available objects in the data directory.

"""
import cherrypy

import backend.global_settings as gloset
from backend.static.make_index import make_index

from util.loggers import BackendLog as bl

class ServerScenesDispatcher:
    """
    A class for deciding what visualization we want to display.

    This loads the actual visualization with control menu and colorbar, without
    any overlay, or it displays a dummy model without colorbar or control menu,
    but with an text overlay.

    """
    def __init__(self):
        """
        Initialise the dispatcher.

        """
        pass

    @cherrypy.expose
    def index(self):
        """
        Return a ``index.html`` file to inform us that we have not selected any
        scenes.

        This method is called if we call ``http://HOST:PORT/scenes(/)``.

        Args:
         None: Nothing.

        Returns:
         str: A string containing the HTML source for generating the
         ``index.html`` file.

        """
        return make_index(
            scene_hash=None,
            with_menu=False, with_colorbar=False,
            overlay_message='No scene selected.'
        )

    def _cp_dispatch(self, vpath):
        """
        Inspect the part of the URL after ``http://HOST:PORT/scenes/`` and
        dispatch an error message or the actual visualization class.

        If the first node is a valid scene_hash we return the actual
        visualization class `ServerDisplayScene`. Otherwise we generate an
        error message.

        Args:
         vpath (list): This contains the segments of the URL after
          ``http://HOST:PORT/scenes/``.

        Returns:
         ServerDisplayScene or error: Return the visualization class or an
         error message.

        """
        # If the first argument is a scene hash ...
        if vpath[0] in gloset.scene_manager.list_scenes()['activeScenes']:

            # ... pop the first argument from the stack (store in calling
            # parameter)
            cherrypy.request.params['scene_hash'] = vpath.pop(0)

            # and return the visualization class (with that calling parameter),
            return ServerDisplayScene()

        # otherwise ...
        else:
            # ... generate an error message
            return self.error

    @cherrypy.expose
    def error(self):
        """
        Return a ``index.html`` file to inform us that we are trying to look at
        a scene that does not exist.

        This method is called if we call
        ``http://HOST:PORT/scenes/INVALID_HASH``, with `INVALID_HASH` being a
        hash that does not exist in the global settings array.

        Args:
         None: Nothing.

        Returns:
         str: A string containing the HTML source for generating the
         ``index.html`` file.

        """
        return make_index(
            scene_hash=None,
            with_menu=False, with_colorbar=False,
            overlay_message='Sorry, this scene does not exist.'
        )


class ServerDisplayScene:
    """
    The class for the actual visualization of scenes that exist in the backend.

    """
    @cherrypy.expose
    def default(self, scene_hash):
        """
        The default site that is displayed with this class.

        This generates a ``index.html`` file that has an existing scene_hash
        encoded.

        Args:
         scene_hash (str): A unique identifier that corresponds to an existing
          scene in the backend.

        Returns:
         str: A string containing the HTML source for generating the
         ``index.html`` file. This has the scene_hash encoded.

        """
        # Return a prepared page
        return make_index(
            scene_hash=scene_hash,
            with_menu=True, with_colorbar=True,
            overlay_message=None
        )
