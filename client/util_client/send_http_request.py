#!/usr/bin/env python3
"""
This sends a HTTP request (POST, GET, DELETE, PATCH, ...) to a server and
returns the response.

"""
import requests
import json


def send_http_request(
        http_method, api_endpoint, connection_data, data_to_transmit
):
    """
    A prototype for sending JSON data to an API endpoint on a target host.

    Args:
     http_method (str, {GET, POST, DELETE, PATCH}): The http method we want to
      employ.
     api_enpoint (str): API endpoint, as in ``http://HOST:PORT/api_endpoint``.
     connection_data (dict): The connection data, containing target address and
      port and program headers containing program name and version.
     data_to_transmit (None or dict): None if we don't want to send data, or
      the data we want to transmit in JSON format. A dict or a ready-formatted
      JSON package will work.

    Returns:
     JSON object (dict) or None: The JSON object (dict) as returned from the
     backend or None, if an error occured.

    Raises:
     TypeError: If one of the input parameters is not of the expected type.
     ValueError: If the `http_method` is not on of GET, POST, DELETE, PATCH.

    """
    if not isinstance(http_method, str):
        raise TypeError('http_method is type {}, is expected to be str'.format(
            type(http_method).__name__))

    # Capitalize
    http_method = http_method.upper()
    if http_method not in ['GET', 'POST', 'DELETE', 'PATCH']:
        raise ValueError('http_method not one of GET, POST, DELETE, PATCH')

    if not isinstance(api_endpoint, str):
        raise TypeError('api_endpoint is type {}, is expected to be str'.
                        format(type(api_endpoint).__name__))

    if not isinstance(connection_data, dict):
        raise TypeError('connection_data is type {}, is expected to be dict'.
                        format(type(connection_data).__name__))

    if not (isinstance(data_to_transmit, dict) or
            isinstance(data_to_transmit, type(None))):
        raise TypeError('data_to_transmit is type {}, is expected to be ' +
                        'dict or None'.format(type(data_to_transmit).__name__))

    # Unpack the connection_data dict
    try:
        host = connection_data['host']
        port = connection_data['port']
        headers = connection_data['headers']
    except KeyError:
        # In case host, port or headers don't exist
        raise ValueError('malformed connection_data -- check that host, ' +
                         'port and headers are contained')

    # Timeout for json requests in seconds
    timeout = 3.5

    target_path = 'http://{}:{}/api/{}'.format(host, port, api_endpoint)

    http_methods = {
        'GET': requests.get,
        'POST': requests.post,
        'PATCH': requests.patch,
        'DELETE': requests.delete
    }

    if http_method in sorted(http_methods.keys()):
        try:
            response = http_methods[http_method](
                url=target_path,
                json=data_to_transmit,
                timeout=timeout,
                headers=headers
            )
            # Check status, if not ok an exception is raised ...
            response.raise_for_status()
        # .. which is then caught.
        except BaseException as e:
            print('{}'.format(e))
            return None

    # Try to parse the response, assuming it is JSON
    try:
        parsed_response = json.loads(response.json())
        return parsed_response
    except TypeError as e:
        print('{}'.format(e))
        print('Client expects JSON response.')
        return None
