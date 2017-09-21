#!/usr/bin/env python3
"""
A small module containing the function for manipulating (listing, deleting,
creating, selecting) scenes on the backend via the client.

"""

import argparse

import os
import sys
sys.path.append('..')
# from client.util_client.post_json import post_json_string
from client.util_client.send_http_request import send_http_request


def scenes_help(c_data):
    """
    Call the scenes function with '-h' for line, so we get the automatic
    documentation from argparse printed out.

    Args:
     c_data (dict): A dictionary containing host, port and headers. This is
      necessary because we essentially call the scenes function and need this
      as an argument for that.

    Returns:
     None, str: Hopefully nothing or a string containing ''.

    Notes:
     This is a bit sketchy, because it should in principle be the same as
     writing ``scenes -h`` in the terminal, but it somehow is not.

    Todo:
     Find a solution for that sketchy behaviour.

    """
    print(scenes('-h', c_data))


def scenes(line, c_data):
    """
    Manipulate the the scenes on the backend server.

    Parse the arguments to a call of ``scenes`` and process them with argparse.
    Call other functions to actually do something (like creating, deleting,
    listing or selecting scenes) afterwards.

    Args:
     line (str): The parsed line from the command line.
     c_data (dict): A dictionary containing host, port and headers.

    Returns:
     None, str: Nothing or an empty string. See notes.

    Notes:
     There is some sketchy behaviour if we try to get the usage message. See
     the notes to scenes_help.

    """
    scenes = argparse.ArgumentParser(
        description='Handle scenes. This means creating, deleting, ' +
        'listing and selecting.',
        prog='scenes')
    subparsers = scenes.add_subparsers(dest='scenes')

    # Add a subparser for listing all the scenes currently available, for
    # creating an empty scene and for deleting a scene.
    list_parser = subparsers.add_parser(
        'list',
        help='List the scenes.'
    )
    list_parser.add_argument('--just', type=str, nargs='+',
                             help='If provided we only list the properties ' +
                             'of this/these scene/s.')

    create_parser = subparsers.add_parser(
        'create',
        help='Create an empty scene.'
    )
    create_parser.add_argument('dataset_list', type=str, nargs='*',
                               help='The id of the object we want to ' +
                               'instantiate the scene with. Valid ' +
                               'identifiers are available via the command ' +
                               '\'objects\'.')

    delete_parser = subparsers.add_parser(
        'delete',
        help='Delete a scene.'
    )
    delete_parser.add_argument('scene_hash', type=str, nargs='*',
                               help='The scene we want to delete. ' +
                               'Requires the full SHA1 hash.')

    select_parser = subparsers.add_parser(
        'select',
        help='Select a scene.'
    )
    select_parser.add_argument('scene_hash', type=str, nargs=1,
                               help='The scene we want to select. ' +
                               'Requires the full SHA1 hash.')

    # Split the string that we get from the terminal on spaces
    line_split = line.split(' ')

    try:
        # Parse the arguments.
        parsed_args = scenes.parse_args(line_split)
    except SystemExit:
        # Something went wrong. argparse will tell us anyway so no need to
        # report anything here.
        #
        # FIXME: When I type 'help scenes' (which essentially is just typing
        # 'scenes -h') I will be presented with a final newline (because of
        # return ''), but when I type 'scenes -h' this does not happen. I have
        # no idea why that's the case.
        return ''

    scenes_action = parsed_args.scenes

    # If we want to list the available scenes
    if scenes_action == 'list':
        just = parsed_args.just
        if just is not None:
            just = clean_list(just)
        scenes_list(c_data, just=just)

    # If we want to create a new and empty scene
    elif scenes_action == 'create':
        dataset_list = parsed_args.dataset_list
        dataset_list = clean_list(dataset_list)
        scenes_create(c_data, dataset_list=dataset_list)

    # If we want to delete a scene
    elif scenes_action == 'delete':
        scene_hash = parsed_args.scene_hash
        scene_hash = clean_list(scene_hash)
        scenes_delete(c_data, scene_hash)

    # If we want to select a scene to perform operations on it
    elif scenes_action == 'select':
        scene_hash = parsed_args.scene_hash
        scenes_select(c_data, scene_hash)

    return None


def clean_list(dirty_list):
    """
    Remove empty entries from a list and cast everything to a string.

    When we parse a string like '    foo' this will land in an array that
    replaces the every _leading_ whitespace into an empty entry in the array.
    Getting rid of those empty entries is the point of this function.

    Args:
     dirty_list (list): A list that potentially has entries that are empty.

    Returns:
     list: A list containing no empty entries, each entry is a string.

    """
    list_length = len(dirty_list)

    for it in range(list_length):
        # Pop all empty entries
        try:
            empty_index = dirty_list.index('')
            dirty_list.pop(empty_index)
        except ValueError:
            continue

    # Tidy up the entries.
    for it, entry in enumerate(dirty_list):
        # Cast to string and remove all '-marks
        dirty_list[it] = str(dirty_list[it])
        dirty_list[it] = dirty_list[it].translate(
            {ord(c): None for c in '\''})

    # For clarity, we want to return something clean.
    clean_list = dirty_list

    return clean_list


def pretty_print_scene(scene_hash, c_data):
    """
    Pretty print a scene.

    Print a scene (and the objects in it) to the screen.

    Args:
     scene_hash (str): The unique identifier of the scene.
     host (str): The address of the backend server, for printing a URL.
     port (int): The port of the backend server, for printing a URL.

    Returns:
     None: Nothing.

    """
    if not isinstance(scene_hash, str):
        raise TypeError('scene_hash is {}, expected str'.format(
            type(scene_hash).__name__))

    if not isinstance(c_data, dict):
        raise TypeError('c_data is {}, expected dict'.format(
            type(c_data).__name__))

    host = c_data['host']
    port = c_data['port']

    datasets_in_scene = send_http_request(
        http_method='GET',
        api_endpoint='scenes/{}'.format(scene_hash),
        connection_data=c_data,
        data_to_transmit=None
    )

    if datasets_in_scene is not None:
        print()             # Newline

        print('Scene {} can be found at'.format(scene_hash))
        print('  http://{}:{}/scenes/{}'. format(
            host, port, scene_hash))

        print('----------------------------------------' +
              '----------------------------------------')

        for entry in datasets_in_scene['loadedDatasets']:
            print('  {} / {}'.format(
                entry['datasetHash'],
                entry['datasetName']))

        print('========================================' +
              '========================================')

        return scene_hash
    else:
        return None


def scenes_list(c_data, just=None):
    """
    List one, several or all scenes.

    Args:
     c_data (dict): A dictionary containing host, port and headers.
     just (None or list, optional, defaults to None): A list of scene_hashes
      of a limited subset of the available scenes, we want to display.

    Returns:
     dict: The returned dictionary.

    """
    if just is not None:
        if not isinstance(just, list):
            raise TypeError('just is {}, expected None or list'.format(
                type(just).__name__))

    response = send_http_request(
        http_method='GET',
        api_endpoint='scenes',
        connection_data=c_data,
        data_to_transmit=None
    )

    if response is None:
        print('Could not get data from the backend.')
        return None

    # Extract activeScenes
    active_scenes = response['activeScenes']

    listed_scenes = []

    if active_scenes == []:
        # If there are no scenes to display on the server
        print('There are no scenes to display.')

    if just is None:
        # If we only want to list a limited amount of scenes
        for scene_hash in active_scenes:
            displayed_scene_hash = pretty_print_scene(
                scene_hash, c_data)
            if displayed_scene_hash is not None:
                listed_scenes.append(displayed_scene_hash)
    else:
        # List everything we have
        for scene_hash in just:
            displayed_scene_hash = pretty_print_scene(
                scene_hash, c_data)
            if displayed_scene_hash is not None:
                listed_scenes.append(displayed_scene_hash)

    return listed_scenes


def scenes_create(c_data, dataset_list):
    """
    Create a new scene.

    If dataset_hash is an empty list, an empty scene will be created. After
    creation a link to the new scene is printed to the screen.

    Args:
     c_data (dict): A dictionary containing host, port and headers.
     dataset_hash (list): A list of objects to include on creation of a new scene.
      Valid object names can be found by typing 'objects'.

    Returns:
     None: Nothing.

    """
    if not isinstance(c_data, dict):
        raise TypeError('c_data is {}, expected dict'.format(
            type(c_data).__name__))

    if not isinstance(dataset_list, list):
        raise TypeError('dataset_list is {}, expected list'.format(
            type(dataset_list).__name__))

    if dataset_list == []:
        print('Can\'t create an empty scene')
        return None

    datasets = {'datasetsToAdd': dataset_list}

    response = send_http_request(
        http_method='POST',
        api_endpoint='scenes',
        connection_data=c_data,
        data_to_transmit=datasets
    )

    if response is None:
        print('Could not create scene')
        return None

    scene_hash = response['sceneHash']
    new_datasets = response['addDatasetsSuccess']
    try:
        failed_datasets = response['addDatasetsFail']
    except KeyError:
        failed_datasets = None

    # host = c_data['host']
    # port = c_data['port']
    # headers = c_data['headers']

    print('Created scene {}'.format(scene_hash))

    pretty_print_scene(scene_hash, c_data)

    if failed_datasets is not None:
        print()
        failed_string = ''
        for dataset in failed_datasets:
            failed_string += dataset + ' '
        print('Could not add the following datasets: {}'.format(failed_string))

    return new_datasets


def scenes_delete(c_data, scene_hash):
    """
    Delete a scene.

    Args:
     c_data (dict): A dictionary containing host, port and headers.
     scene_hash (list): A list of unique identifier(s) of the scene(s) that
      should be deleted.

    Returns:
     None: Nothing.

    Todo:
     Print feedback?

    """
    api_call = 'scenes_delete'
    for scene in scene_hash:
        data = {'scene_hash': scene}
        post_json_string(
            api_call=api_call, data=data, connection_data=c_data)

    return None


def scenes_select(c_data, scene_hash):
    """
    Select a scene.

    Args:
     c_data (dict): A dictionary containing host, port and headers.
     scene_hash (str): The unique identifier of the scene that should be
      selected.

    Returns:
     None: Nothing.

    Todo:
     Expand this. This is the entry point for manipulating anything IN a given
     scene.

    """
    api_call = 'scenes_select'
    data = None
    answer = post_json_string(
        api_call=api_call, data=data, connection_data=c_data)

    return None
