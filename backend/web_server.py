#!/usr/bin/env python3
"""
The web server class. This will host a web server at a given port.
"""

import os

# conda install cherrypy
import cherrypy

from backend.web_server_class import ServerRoot, ServerScenes, ServerAPI
import backend.global_settings as global_settings


class Web_Server:
    """
    Host a web server on a given port and hand out the files in the path.
    """

    def __init__(self, frontend_directory, data_directory, port=8008):
        """
        Initialise the webserver.
        """

        control_path = os.path.join(frontend_directory, 'control')
        display_path = os.path.join(frontend_directory, 'display')

        print(control_path, display_path)
        self.conf = {
            '/': {
                'tools.gzip.on': True,
                'tools.staticdir.on': True,
                'tools.staticdir.dir': control_path,
                'tools.staticdir.index': 'index.html'
            },
            '/scenes': {
                'tools.gzip.on': True,
                'tools.staticdir.on': True,
                'tools.staticdir.dir': display_path,
                'tools.staticdir.index': 'index.html'
            },
            '/api': {
                'tools.gzip.on': True
            }
        }
        self.port = port
        self.data_directory = data_directory

        # Initialise the global variables. For later use just import the
        # backend.global_settings and write to the global_scenes array.
        global_settings.init()

    def start(self):
        """
        Start the web server on the given port with the given config.
        """

        # Set the port
        cherrypy.config.update(
            {'server.socket_port': self.port,
             'server.socket_host': '0.0.0.0'
            }
        )

        # Load the server class for displaying fem data
        cherrypy.tree.mount(
            ServerRoot(), '/', self.conf)
        cherrypy.tree.mount(
            ServerScenes(), '/scenes', self.conf)
        cherrypy.tree.mount(
            ServerAPI(data_directory=self.data_directory), '/api', self.conf)

        # Start the server
        cherrypy.engine.start()
        cherrypy.engine.block()
