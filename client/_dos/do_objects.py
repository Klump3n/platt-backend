#!/usr/bin/env python3
"""
List all the available simulation data directories.
"""

from util.post_json import post_json_string

def objects(c_data):
    """
    List all the available simulation data directories.
    """

    # Call the host and ask for simulation data
    api_call = 'list_of_fem_data'
    data = ''
    response = post_json_string(
        api_call=api_call, data=data, connection_data=c_data)

    # Try to parse the available simulation files
    try:
        object_folders = response['data_folders']
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
