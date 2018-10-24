#!/usr/bin/env python3
"""
Start a web server. Direct your browser to [HOST_IP]:[PORT] with PORT being
either 8008 or the supplied value.

"""
import os
import sys
import argparse
import pathlib

from util.version import version
import backend.web_server as web_server


def parse_commandline():
    """
    Parse the command line and return the parsed arguments in a namespace.

    Args:
     None: No parameters.

    Returns:
     namespace: A namespace containing all the parsed command line arguments.

    Notes:
     The default port for the web server is contained in this function.

    """
    # HACK: Under certain conditions we don't want to supply a --data_dir (e.g.
    # if we just want the version returned), but we still want to set it to
    # required while parsing the command line. The following will give True if
    # we neither want to test nor have the version printed out, but False
    # otherwise.
    no_data_dir_requirements = (
        '--test' not in sys.argv and
        '--version' not in sys.argv and
        '-v' not in sys.argv
    )
    external_data_source_requirements = (
        '-e' in sys.argv or
        '--external' in sys.argv
    )

    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument(
        '-p', '--port', default=8008,
        help='The port for the web server.')

    source_group = parser.add_mutually_exclusive_group(
        # NOTE: see the comment above the declaration of
        # no_data_dir_requirements
        required=no_data_dir_requirements)
    source_group.add_argument(
        '-d', '--data-dir',
        help='The directory in which we want to look for simulation data.'
    )
    source_group.add_argument(
        '-e', '--external', action='store_true',
        help='Use an external data source.'
    )

    parser.add_argument(
        '--ext_address', required=external_data_source_requirements,
        help='IP address of the external data source'
    )
    parser.add_argument(
        '--ext_port', required=external_data_source_requirements,
        help='Port of the external data source'
    )

    parser.add_argument('--test', action='store_true',
                        help='Perform a unit test.')
    parser.add_argument('-v', '--version', action='store_true',
                        help='Display the program name and version.')
    args = parser.parse_args()

    return args


def start_backend(data_dir, port, ext_addr, ext_port):
    """
    Start the backend on the provided port, serving simulation data from the
    provided directory or from the external source.

    Set the working directory to the program directory and display a welcome
    message, containing the program name and version along with the server
    port and the directories for the frontend and the simulation data. Finally,
    start an instance of the cherrypy ``Web_Server`` class.

    Args:
     data_dir (string): The path to the simulation data, either relative to the
      main.py file or absolute.
     port (int): The port for the web server.
     ext_addr(str): The IP address of the external source.
     ext_port (int): The network port of the external source.

    Returns:
     None: Nothing

    """
    # Get the version information
    version_info = version()
    program_name = version_info['programName']
    version_number = version_info['programVersion']

    # Settings for the server
    #
    # Convert paths to os.PathLike
    working_dir = pathlib.Path(__file__).cwd()
    frontend_dir = working_dir / 'frontend'

    # Define the source of the data
    data_source = None

    if data_dir:
        data_dir = pathlib.Path(data_dir)
        data_source = 'local'

    if ext_addr and ext_port:
        data_source = 'external'

    source_dict = {
        'source': data_source,
        'local': data_dir,
        'external': {
            'addr': ext_addr,
            'port': ext_port
        }
    }

    # Change working directory in case we are not there yet
    os.chdir(working_dir)

    # Welcome message
    welcome_msg = ''
    welcome_msg += '\nThis is {program_name} {version_number}\n'\
                   'Starting http server on port {port_text}\n\n'\
                   'Serving frontend from directory '\
                   '{frontend_dir_text}\n'.format(
                       program_name=program_name,
                       version_number=version_number,
                       port_text=port,
                       frontend_dir_text=frontend_dir
                   )

    if data_source == 'local':
        welcome_msg += 'Will search for simulation data in local directory '\
                       '{data_dir_text}\n'.format(
                           data_dir_text=data_dir
                       )

    if data_source == 'external':
        welcome_msg += 'Serving data from external source at '\
                       '{ext_addr_text}:{ext_port_text}\n'.format(
                           ext_addr_text=ext_addr,
                           ext_port_text=ext_port
                       )

    print(welcome_msg)

    # Instanciate and start the backend.
    web_instance = web_server.Web_Server(
        frontend_directory=frontend_dir,
        port=port,
        source_dict=source_dict
    )
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
    just_print_version = ARGS.version
    port = ARGS.port

    # Init the source
    data_dir = None
    ext_addr = None
    ext_port = None

    if ARGS.data_dir:
        data_dir = ARGS.data_dir

    if ARGS.external:
        ext_addr = ARGS.ext_address
        ext_port = ARGS.ext_port

    # Just print the version?
    if just_print_version:
        print_version()

    # Perform a unit test?
    if do_unittest:
        import unittest
        tests = unittest.TestLoader().discover('.')
        unittest.runner.TextTestRunner(verbosity=2, buffer=True).run(tests)

        sys.exit('\nPerformed unittests -- exiting.')

    # Start the program
    start_backend(data_dir, port, ext_addr, ext_port)

    return None


def print_version():
    """
    Print the program name and version and exit the program.

    Args:
     None: No parameters.

    Returns:
     None: Nothing.

    """
    # Get the version information
    version_info = version()
    program_name = version_info['programName']
    version_number = version_info['programVersion']

    sys.exit('{} {}'.format(program_name, version_number))

    return None


if __name__ == '__main__':
    """
    This is called when (i.e. always) we start this file as a standalone
    version.

    """
    # Start the program
    start_program()
