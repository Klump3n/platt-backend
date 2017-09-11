#!/usr/bin/env python3
"""
This sends a HTTP request (POST, GET, DELETE, PATCH, ...) to a server and
returns the response.

"""
import requests


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
     data_to_transmit (None or dict): None if we don't want to send data or the
      data we want to transmit in JSON format. A dict or a ready-formatted JSON
      package will work.

    Returns:
     JSON object, dict: The JSON object as returned from the backend.

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

    if not (not isinstance(data_to_transmit, dict) and
            isinstance(data_to_transmit, type(None))):
        raise TypeError('data_to_transmit is type {}, is expected to be ' +
                        'dict or None'.format(type(data).__name__))

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

    target_path = 'http://{}:{}/api/{}'.format(host, port, api_endpoint)

    # GET method
    if http_method == 'GET':
        try:
            response = requests.get(
                url=target_path,
                json=data_to_transmit,
                timeout=timeout,
                headers=headers
            )
            response.raise_for_status()
        except BaseException as e:
            print('{}'.format(e))
            return None

    # POST method
    if http_method == 'POST':
        try:
            response = requests.post(
                url=target_path,
                json=data_to_transmit,
                timeout=timeout,
                headers=headers
            )
            response.raise_for_status()
        except BaseException as e:
            return '{}'.format(e)

    # PATCH method
    if http_method == 'PATCH':
        response = requests.patch(
            url=target_path,
            json=data_to_transmit,
            timeout=timeout,
            headers=headers
        )

    # DELETE method
    if http_method == 'DELETE':
        response = requests.delete(
            url=target_path,
            json=data_to_transmit,
            timeout=timeout,
            headers=headers
        )

    return response
