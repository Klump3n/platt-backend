#!/usr/bin/env python3
"""
The control interface for the web server. This should be seen as support for
the client program.

So far there is no functionality. It serves as a reminder.

"""

import cherrypy

import backend.global_settings as gloset


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
