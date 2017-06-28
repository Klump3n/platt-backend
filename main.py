#!/usr/bin/env python3

"""
Start a web server. Direct your browser to [HOST_IP]:[PORT] with PORT being
either 8008 or the supplied value.
"""

import os
import sys
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

    # Perform a unit test
    if ARGS.test:
        import unittest
        tests = unittest.TestLoader().discover('.')
        unittest.runner.TextTestRunner(verbosity=2).run(tests)

        sys.exit('Performed unittests -- exiting.')

    # Start the program
    start_backend(ARGS)


