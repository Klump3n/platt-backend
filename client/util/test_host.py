#!/usr/bin/env python3
"""
Check the target host.
"""

from util.post_json import post_json_string

def target_online_and_compatible(c_data, version_dict):
    """
    Check whether or not we are dealing with a compatible server that is online.
    """

    api_call = 'connect_client'
    # Call the about page of the host
    response = post_json_string(
        api_call=api_call, connection_data=c_data)

    # Check if we see what we want to see
    expected_version_response = version_dict['version']

    if ('Failed to establish a new connection' in response):
        print('No active server found.')
        return False

    elif (response['version'] != expected_version_response):
        warning_text = ('Server/client version mismatch. Do not expect '+
                        'functionality.')
        print(warning_text)
        # warning_text = textwrap.wrap(
        #     'The host does not appear to support what we would like ' +
        #     'him to do. Do not expect any functionality.')
        # for line in warning_text:
        #     print(line)
        # print()             # Newline
        return False

    else:
        return True
