#!/usr/bin/env python3
"""
A small module containing the function for getting the available simulation
data from the backend and displaying it in the client.

"""
from client.util_client.send_http_request import send_http_request
from client.util_client.print_function_usage import print_help


def datasets_help():
    """
    Print the help message for the objects function.

    """
    help_text = """
    List all the available simulation data directories.
    """

    print_help(help_text)

    return None


def datasets(c_data):
    """
    List all the available simulation data directories.

    Sends an empty HTTP GET request to the ``api/datasets``. The returned
    response is then parsed and printed out nicely formatted. In case of an
    exception (that means no response is returned) a message is printed to the
    screen, informing us that no response came back.

    Args:
     c_data (dict): A dictionary containing the connection data. That is, a
      target host, target port and a header.

    Returns:
     dict: The dictionary obtained from the backend.

    See Also:
     :py:obj:`backend.web_server_api.ServerAPI.list_of_fem_data`

    """
    response = send_http_request(
        http_method='GET',
        api_endpoint='datasets',
        connection_data=c_data,
        data_to_transmit=None
    )

    if response is None:
        print('No data returned')
        return None

    # Try to parse whatever came back
    try:
        available_datasets = response['availableDatasets']
        print('A list of valid datasets is:')
        print()
        for dataset in available_datasets:
            print('  \'{}\''.format(dataset))
        print()

    except KeyError:
        print('Returned data could not be processed')
        return None

    return response
