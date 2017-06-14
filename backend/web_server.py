#!/usr/bin/env python3
"""
The web server class. This will host a web server at a given port.
"""

# conda install cherrypy
import cherrypy

from backend.web_server_class import APIEndPoint
import backend.global_settings as global_settings


class Web_Server:
    """
    Host a web server on a given port and hand out the files in the path.
    """

    def __init__(self, frontend_directory, data_directory, port=8008):
        """
        Initialise the webserver.
        """

        self.conf = {
            '/': {
                'tools.gzip.on': True,
                'tools.staticdir.on': True,
                'tools.staticdir.dir': frontend_directory,
                'tools.staticdir.index': 'index.html'
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
            {'server.socket_port': self.port}
        )

        # Load the server class for displaying fem data
        cherrypy.tree.mount(
            APIEndPoint(data_directory=self.data_directory), '/', self.conf)

        # Start the server
        cherrypy.engine.start()
        cherrypy.engine.block()
