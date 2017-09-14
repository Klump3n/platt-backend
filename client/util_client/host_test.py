#!/usr/bin/env python3
"""
Check the target host.

"""
from util_client.send_http_request import send_http_request


def target_online_and_compatible(c_data):
    """
    Check whether or not we are dealing with a compatible server that is
    online.

    Args:
     c_data (dict): A dictionary containing target host and port as well as a
      header with a user-agent, which we use to figure out which backend
      version we hope to find.

    Returns:
     bool: False if the backend is not responding or is running a different
     version than the client and True if the backend is online and has the
     same version as the client.

    See Also:
     :py:meth:`backend.web_server_api.ServerAPI.connect_client`

    """
    # Get the version from the server
    response = send_http_request(
        http_method='GET',
        api_endpoint='version',
        connection_data=c_data,
        data_to_transmit=None
    )

    if response is None:
        print('Invalid response from server.')
        return False

    # Check if we see what we want to see. Get the version out of the headers
    # user-agent.
    expected_version_response = c_data['headers']['user-agent'].split('/')[1]

    if ('Failed to establish a new connection' in response):
        print('No active server found.')
        return False

    # If the backend version is not as expected
    elif (response['programVersion'] != expected_version_response):
        warning_text = ('Server/client version mismatch. Do not expect ' +
                        'functionality.')
        print(warning_text)
        return False

    else:
        return True
