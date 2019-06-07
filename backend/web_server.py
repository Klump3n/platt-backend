#!/usr/bin/env python3
"""
The web server class. This will host a web server at a given port.

"""
import os
import asyncio
from contextlib import suppress

# conda install cherrypy
import cherrypy

import logging.config

from ws4py.server.cherrypyserver import WebSocketTool

from backend.web_server_api import ServerAPI
from backend.web_server_websocket import (
    WebSocketHandler, WebSocketAPI, SceneManagerPlugin)
from backend.web_server_control import ServerRoot
from backend.web_server_display import ServerScenesDispatcher
import backend.global_settings as global_settings

from util.loggers import BackendLog as bl


class Web_Server:
    """
    Host a web server on a given port and hand out the files in the path.

    On initialising it sets the path to the control interface directory and to
    the directory that contains the visualization. It also sets the
    configurations for the control interface, for the visualization and for
    the API. Finally, it initializes the global settings module.

    Args:
     frontend_directory (str): The path to the frontend.
     data_directory (str): The path to the directory, that contains the
      simulation data.
     port (int, optional, defaults to 8008): The port on which the
      backend listens to connections.

    Todo:
     Replace path strings with Pathlike objects.

    Notes:
     The global_settings module is initialized in __init__().

    """
    def __init__(
            self,
            # web_server_shutdown_event,
            frontend_directory, port=8008,
            source_dict=None
    ):
        """
        Initialise the webserver.

        Set the path to the control interface directory and to the directory
        that contains the visualization. Set the configurations for the control
        interface, for the visualization and for the API. Finally, initialize
        the global settings module.

        Args:
         frontend_directory (str): The path to the frontend.
         data_directory (os.PathLike): The path to the directory, that contains
          the simulation data.
         port (int, optional, defaults to 8008): The port on which the
          backend listens to connections.
         ext_addr (str): IP address of the external source.
         ext_port (int): Network port of the external source.

        Returns:
         None: Nothing.

        """
        # self._web_server_shutdown_event = web_server_shutdown_event

        # # create a new event loop
        # self._loop = asyncio.new_event_loop()
        # asyncio.set_event_loop(self._loop)

        # start_server_task = self._loop.create_task(
        #     self._start_server_coro())

        # watch_server_stop_task = self._loop.create_task(
        #     self._watch_server_stop_coro())

        # self.tasks = [
        #     start_server_task,
        #     watch_server_stop_task
        # ]

        self._source_dict = source_dict

        control_path = os.path.join(frontend_directory, 'control')
        display_path = os.path.join(frontend_directory, 'display')

        self._root_conf = {
            '/': {
                'tools.gzip.on': True,
                'tools.staticdir.on': True,
                'tools.staticdir.dir': control_path,
                'tools.staticdir.index': 'index.html'
            }
        }

        self._scenes_conf = {
            '/': {
                'tools.gzip.on': True,
                # 'tools.staticdir.debug' : True,
                'tools.staticdir.on': True,
                'tools.staticdir.dir': display_path
                # No default file. The index file is provided by the dispatcher.
            }
        }

        self._api_conf = {
            '/': {
                'tools.gzip.on': True
            }
        }

        self._websocket_conf = {
            '/': {
                'tools.websocket.on': True,
                'tools.websocket.handler_cls': WebSocketHandler
            }
        }

        self.port = port

        # self.start()

    def start(self):
        """
        Start the web server with the parameters that were set upon
        initialization.

        This mounts three different servers:

        * one that serves the configuration menu on ``http://HOST:PORT/``. The
          server class rests in ``backend.web_server_control``.
        * one that serves the visualization on ``http://HOST:PORT/scenes``. The
          server class rests in ``backend.web_server_display``.
        * one for the API endpoint on ``http://HOST:PORT/api``. The server
          class rests in ``backend.web_server_api``.

        Args:
         None: No parameters.

        Returns:
         None: Nothing.

        Notes:
         After this method is called, no further commands will be evaluated
         until after the backend is shut down.

        """
        # Initialise the global variables. For later use just import the
        # backend.global_settings and use the scene manager from there.
        global_settings.init(source_dict=self._source_dict)

        # Set the port
        cherrypy.config.update(
            {'server.socket_port': self.port,
             'server.socket_host': '0.0.0.0'  # Can be reached from everywhere
            }
        )

        bl.debug("Subscribing to SceneManagerPlugin")
        # Add the SceneManagerPlugin to the server bus
        SceneManagerPlugin(cherrypy.engine).subscribe()

        bl.debug("Adding WebSocketTool")
        cherrypy.tools.websocket = WebSocketTool()

        # Load the server class for displaying fem data
        cherrypy.tree.mount(
            ServerRoot(), '/', self._root_conf)
        cherrypy.tree.mount(
            ServerScenesDispatcher(), '/scenes', self._scenes_conf)
        cherrypy.tree.mount(
            ServerAPI(), '/api', self._api_conf)
        cherrypy.tree.mount(
            WebSocketAPI(), '/websocket', self._websocket_conf)

        cherrypy.config.update({'log.screen': True,
                                'log.access_file': '',
                                'log.error_file': ''})
        cherrypy.engine.unsubscribe('graceful', cherrypy.log.reopen_files)
        cherrypy.engine.subscribe('exit', self._stop)

        # Start the server
        bl.debug("Starting engine")
        cherrypy.engine.start()
        bl.debug("Blocking engine")
        cherrypy.engine.block()

        return None

    def _stop(self):
        """
        Send a stop message to the proxy.

        """
        if self._source_dict["source"] == "external":
            gwc_dict = self._source_dict["external"]["comm_dict"]
            shutdown_event = gwc_dict["shutdown_platt_gateway_event"]
            shutdown_event.set()

