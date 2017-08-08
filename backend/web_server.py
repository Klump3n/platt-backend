#!/usr/bin/env python3
"""
The web server class. This will host a web server at a given port.
"""

import os

# conda install cherrypy
import cherrypy

from backend.web_server_display import ServerRoot, ServerScenesDispatcher
# from backend.old_web_server_api import OLDServerAPI
from backend.web_server_api import ServerAPI
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

        self.root_conf = {
            '/': {
                'tools.gzip.on': True,
                'tools.staticdir.on': True,
                'tools.staticdir.dir': control_path,
                'tools.staticdir.index': 'index.html'
            }
        }

        self.scenes_conf = {
            '/': {
                'tools.gzip.on': True,
                # 'tools.staticdir.debug' : True,
                'tools.staticdir.on': True,
                'tools.staticdir.dir': display_path
                # No default file. The index file is provided by the dispatcher.
            }
        }

        self.api_conf = {
            '/': {
                'tools.gzip.on': True
            }
        }

        self.port = port
        self.data_directory = data_directory

        # Initialise the global variables. For later use just import the
        # backend.global_settings and use the scene manager from there.
        global_settings.init(data_dir=self.data_directory)

    def start(self):
        """
        Start the web server on the given port with the given config.
        """

        # Set the port
        cherrypy.config.update(
            {'server.socket_port': self.port,
             'server.socket_host': '0.0.0.0'  # Can be reached from everywhere
            }
        )

        # Load the server class for displaying fem data
        cherrypy.tree.mount(
            ServerRoot(), '/', self.root_conf)
        cherrypy.tree.mount(
            ServerScenesDispatcher(), '/scenes', self.scenes_conf)
        # cherrypy.tree.mount(
        #     OLDServerAPI(data_directory=self.data_directory), '/api', self.api_conf)
        cherrypy.tree.mount(
            ServerAPI(), '/api', self.api_conf)

        # Start the server
        cherrypy.engine.start()
        cherrypy.engine.block()
