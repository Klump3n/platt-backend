#!/usr/bin/env python3
"""
A small module containing the function for getting the available simulation
data from the backend and displaying it in the client.

"""

from util_client.post_json import post_json_string
from util_client.send_http_request import send_http_request
from util_client.print_function_usage import print_help


def objects_help():
    """
    Print the help message for the objects function.

    """
    help_text = """
    List all the available simulation data directories.
    """

    print_help(help_text)

    return None


def objects(c_data):
    """
    List all the available simulation data directories.

    Sends an empty JSON request to the ``api/list_of_fem_data``. The returned
    response is then parsed and printed out nicely formatted. In case of an
    exception (that means no response is returned) a message is printed to the
    screen, informing us that no response came back.

    Args:
     c_data (dict): A dictionary containing the connection data. That is, a
      target host, target port and a header.

    Returns:
     None: Nothing

    See Also:
     :py:obj:`backend.web_server_api.ServerAPI.list_of_fem_data`

    """
    response = send_http_request(
        http_method='GET',
        api_endpoint='datasets',
        connection_data=c_data,
        data_to_transmit=None
    )

    # Try to parse the available simulation files
    try:
        object_folders = response['availableDatasets']
        print('A list of valid objects is:')
        print()
        for folder in object_folders:
            print('  \'{}\''.format(folder))
        print()

    # If none are returned, so be it
    except:
        print('No data returned.')

    # Return nothing
    return None
