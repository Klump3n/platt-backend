#!/usr/bin/env python3

"""
Start a web server. Direct your browser to [HOST_IP]:[PORT] with PORT being
either 8008 or the supplied value.
"""

import os
import argparse
import backend.web_server as web_server


def parse_commandline():
    """
    Parse the command line and return the parsed arguments.
    """

    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument(
        '-p', '--port', default=8008,
        help='The port for the web server.')
    parser.add_argument(
        '-d', '--data-dir', required=True,
        help='The directory in which we want to look for simulation data.')
    args = parser.parse_args()

    return args

def start_backend(args):
    """
    Start the backend.
    """

    # Settings for the server
    data_dir = os.path.abspath(args.data_dir)

    working_dir = os.path.dirname(os.path.realpath(__file__))
    frontend_dir = os.path.join(working_dir, 'frontend')

    # Change working directory in case we are not there yet
    os.chdir(working_dir)

    port = args.port

    # Welcome message
    start_msg = 'Starting http server on port {port_text}\n\n'\
                'Serving frontent from directory {frontend_dir_text}\n'\
                'Will search for simulation data in directory {data_dir_text}'\
                '\n'.format(
                    port_text=port,
                    frontend_dir_text=frontend_dir,
                    data_dir_text=data_dir)
    print(start_msg)

    # Instanciate and start the backend.
    web_instance = web_server.Web_Server(
        frontend_directory=frontend_dir,
        data_directory=data_dir,
        port=port)
    web_instance.start()


# Start the program
if __name__ == '__main__':
    """
    This is called when (i.e. always) we start this file as a standalone
    version.
    """

    # Parse the command line arguments
    ARGS = parse_commandline()
    # Start the program
    start_backend(ARGS)


