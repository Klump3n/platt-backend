#!/usr/bin/env python3
"""
Start a web server. Direct your browser to [HOST_IP]:[PORT] with PORT being
either 8008 or the supplied value.

"""
import os
import sys
import time
import argparse
import pathlib
import queue
import asyncio
import threading

from util.version import version
from util.greet import greeting
from util.loggers import GatewayLog as gl, BackendLog as bl

import backend.web_server as web_server
import backend.platt_proxy_client as platt_client
import backend.proxy_services as ps


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
    version_test_requirements = (
        '--test' not in sys.argv and
        '--version' not in sys.argv and
        '-v' not in sys.argv
    )

    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )

    parser.add_argument(
        "-l", "--log",
        help="Set the logging level",
        default="info",
        choices=["debug", "info", "warning", "error", "critical", "quiet"]
    )

    parser.add_argument(
        '-p', '--port', default=8008,
        help='The port for the web server.')

    parser.add_argument(
        '--gw_address', required=version_test_requirements,
        help='Address of the platt gateway'
    )
    parser.add_argument(
        '--gw_port', required=version_test_requirements,
        help='Port of the platt gateway',
        default=8009
    )

    parser.add_argument('--test', action='store_true',
                        help='Perform a unit test.')
    parser.add_argument('-v', '--version', action='store_true',
                        help='Display the program name and version.')
    args = parser.parse_args()

    return args


def start_backend(port, ext_addr, ext_port):
    """
    Start the backend on the provided port, serving simulation data from the
    provided external source.

    Set the working directory to the program directory and display a welcome
    message, containing the program name and version along with the server
    port and the directories for the frontend and the simulation data. Finally,
    start an instance of the cherrypy ``Web_Server`` class.

    Args:
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

    platt_gateway = None
    gateway_comm_dict = dict()
    if ext_addr and ext_port:
        data_source = 'external'

        # event that can be queried if the connection to the proxy is active
        proxy_connection_active_event = threading.Event()
        # queue for pushing information about new files over the socket
        tell_new_file_queue = queue.Queue()
        with tell_new_file_queue.mutex:
            tell_new_file_queue.queue.clear()
        # index request event
        get_index_event = threading.Event()
        # index data queue (answer to request event)
        receive_index_data_queue = queue.Queue()
        with receive_index_data_queue.mutex:
            receive_index_data_queue.queue.clear()
        # queue for requesting files
        file_request_queue = queue.Queue()
        with file_request_queue.mutex:
            file_request_queue.queue.clear()
        # queue for receiving file contents, name and hash after requesting them
        file_contents_name_hash_queue = queue.Queue()
        with file_contents_name_hash_queue.mutex:
            file_contents_name_hash_queue.queue.clear()
        # shutdown the platt gateway
        shutdown_platt_gateway_event = threading.Event()

        gateway_comm_dict["proxy_connection_active_event"] = proxy_connection_active_event
        gateway_comm_dict["tell_new_file_queue"] = tell_new_file_queue
        gateway_comm_dict["get_index_event"] = get_index_event
        gateway_comm_dict["get_index_data_queue"] = receive_index_data_queue
        gateway_comm_dict["file_request_queue"] = file_request_queue
        gateway_comm_dict["file_contents_name_hash_queue"] = file_contents_name_hash_queue
        gateway_comm_dict["shutdown_platt_gateway_event"] = shutdown_platt_gateway_event

        platt_gateway = threading.Thread(
            target=platt_client.Client,
            name="GatewayClient",
            args=(
                ext_addr,
                ext_port,
                proxy_connection_active_event,
                tell_new_file_queue,
                get_index_event,
                receive_index_data_queue,
                file_request_queue,
                file_contents_name_hash_queue,
                shutdown_platt_gateway_event
            )
        )

        proxy_services = threading.Thread(
            target=ps.ProxyServices,
            name="ProxyServices",
            args=(
                [
                    gateway_comm_dict
                ]
            )
        )

    source_dict = {
        'source': data_source,
        # 'local': data_dir,
        'external': {
            'addr': ext_addr,
            'port': ext_port,
            "comm_dict": gateway_comm_dict
        }
    }

    # Change working directory in case we are not there yet
    os.chdir(working_dir)

    # Welcome message
    welcome_msg = str()
    welcome_msg += greeting
    welcome_msg += '\nThis is {program_name} {version_number}\n'\
                   'Starting http server on port {port_text}\n\n'\
                   'Serving frontend from directory '\
                   '{frontend_dir_text}\n'.format(
                       program_name=program_name,
                       version_number=version_number,
                       port_text=port,
                       frontend_dir_text=frontend_dir
                   )

    welcome_msg += 'Serving data from external source at '\
                   '{ext_addr_text}:{ext_port_text}\n'.format(
                       ext_addr_text=ext_addr,
                       ext_port_text=ext_port
                   )

    print(welcome_msg)

    winst = web_server.Web_Server(
        frontend_dir,
        port,
        source_dict
    )

    if platt_gateway:
        platt_gateway.start()
        proxy_services.start()

    winst.start()


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

    ext_addr = ARGS.gw_address
    ext_port = ARGS.gw_port

    # Just print the version?
    if just_print_version:
        print_version()

    # Perform a unit test?
    if do_unittest:
        import unittest
        tests = unittest.TestLoader().discover('.')
        unittest.runner.TextTestRunner(verbosity=2, buffer=True).run(tests)

        sys.exit('\nPerformed unittests -- exiting.')

    # start the different loggers
    setup_logging(ARGS.log)

    # Start the program
    start_backend(port, ext_addr, ext_port)

    return None


def setup_logging(logging_level):
    """
    Setup the loggers.

    """
    gl(logging_level)           # setup simulation logging
    gl.info("Started Gateway logging with level '{}'".format(logging_level))
    bl(logging_level)           # setup backend logging
    bl.info("Started Backend logging with level '{}'".format(logging_level))


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
