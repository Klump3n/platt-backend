#!/usr/bin/env python3
"""
Post a JSON string to the server.

"""

import requests


def post_json_string(
        api_call, connection_data,
        data=None
):
    """
    Prototype for sending a post request with error handling and so on.

    Send a JSON file `data` to ``http://HOST:PORT/api_call`` (`host` and `port`
    from `connection_data`).

    Args:
     api_call (str): API endpoint, as in ``http://HOST:PORT/api_call``.
     connection_data (dict): The connection data, containing target address and
      port and program headers containing program name and version.
     data (dict, None): The data we want to transmit in JSON format. A dict or
      a ready-formatted JSON package will work.

    Returns:
     JSON object, dict: The JSON object as returned from the backend.

    Raises:
     TypeError: If one of the input parameters is not of the expected type.

    """
    if not isinstance(api_call, str):
        raise TypeError('api_call is type {}, is expected to be str'.format(
            type(api_call).__name__))

    if not isinstance(connection_data, dict):
        raise TypeError('connection_data is type {}, is expected to be dict'.
                        format(type(connection_data).__name__))

    if not isinstance(data, dict) and not isinstance(data, type(None)):
        raise TypeError('data is type {}, is expected to be dict or NoneType'.
                        format(type(data).__name__))

    # Unpack the connection_data dict
    try:
        host = connection_data['host']
        port = connection_data['port']
        headers = connection_data['headers']
    except KeyError:
        # In case host, port or headers don't exist
        print('connection_data does not contain the data we expect.')

    # Timeout for json requests
    timeout = 3.5

    # Try to send the JSON file.
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
