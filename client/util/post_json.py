#!/usr/bin/env python3
"""
Post a JSON string to the server.
"""

import requests

def post_json_string(
        api_call, connection_data,
        data=''
):
    """
    Prototype for sending a post request with error handling and so on.
    """

    # Unpack the c_data dict
    host = connection_data['host']
    port = connection_data['port']
    headers = connection_data['headers']

    # Timeout for json requests
    timeout = 3.5

    try:
        api_call = api_call
        url = 'http://{}:{}/api/{}'.format(host, port, api_call)
        response = requests.post(
            url=url,
            json=data,
            timeout=timeout,
            headers=headers
        )

        response.raise_for_status()
    except BaseException as e:
        return '{}'.format(e)

    return response.json()

