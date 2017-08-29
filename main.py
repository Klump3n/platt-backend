#!/usr/bin/env python3

"""
Start a web server. Direct your browser to [HOST_IP]:[PORT] with PORT being
either 8008 or the supplied value.
"""

import os
import sys
import argparse
from util.version import version
import backend.web_server as web_server


def parse_commandline():
    """
    Parse the command line and return the parsed arguments in a namespace.

    Args:
     None: No parameters.

    Returns:
     namespace: A namespace containing all the parsed command line arguments.
    """

    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument(
        '-p', '--port', default=8008,
        help='The port for the web server.')
    parser.add_argument(
        # NOTE: the term behind 'required' gives either True or False depending
        # on whether --test is present in sys.argv or not. This is a small hack
        # for not having to supply --data-dir when we do a test but still kind
        # of setting it to required.
        '-d', '--data-dir', required='--test' not in sys.argv,
        help='The directory in which we want to look for simulation data.')
    parser.add_argument('--test', action='store_true',
                        help='Perform a unit test.')
    args = parser.parse_args()

    return args


def start_backend(data_dir, port=8008):
    """
    Start the backend on the provided port, serving simulation data from the
    provided directory.

    Set the working directory to the program directory and display a welcome
    message, containing the program name and version along with the server
    port and the directories for the frontend and the simulation data. Finally,
    start an instance of the cherrypy ``Web_Server`` class.

    Args:
     data_dir (string): The path to the simulation data, either relative to the
      main.py file or absolute.
     port (int, optional, defaults to `8008`): The port for the web server.

    Returns:
     None: Nothing
    """

    # Get the version information
    version_info = version()
    program_name = version_info['program']
    version_number = version_info['version']

    # Settings for the server
    data_dir = os.path.abspath(data_dir)

    working_dir = os.path.dirname(os.path.realpath(__file__))
    frontend_dir = os.path.join(working_dir, 'frontend')

    # Change working directory in case we are not there yet
    os.chdir(working_dir)

    # port = args.port

    # Welcome message
    start_msg = '\nThis is {program_name} {version_number}\n'\
                'Starting http server on port {port_text}\n\n'\
                'Serving frontent from directory {frontend_dir_text}\n'\
                'Will search for simulation data in directory {data_dir_text}'\
                '\n'.format(
                    program_name=program_name,
                    version_number=version_number,
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

    return None


def start_program():
    """
    Start the program.

    Parse the command line and either perform a unit test or start the backend
    with the parameters that have been parsed from the command line.

    Args:
     None: No parameters.

    Returns:
     None: Nothing

    """

    # Parse the command line arguments
    ARGS = parse_commandline()

    # Extract the command line arguments
    do_unittest = ARGS.test
    port = ARGS.port
    data_dir = ARGS.data_dir

    # Perform a unit test?
    if do_unittest:
        import unittest
        tests = unittest.TestLoader().discover('.')
        unittest.runner.TextTestRunner(verbosity=2).run(tests)

        sys.exit('\nPerformed unittests -- exiting.')

    # Start the program
    start_backend(data_dir, port)

    return None


if __name__ == '__main__':
    """
    This is called when (e.g. always) we start this file as a standalone
    version.
    """

    # Start the program
    start_program()
