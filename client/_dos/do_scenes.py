#!/usr/bin/env python3
"""
A small module containing the function for manipulating (listing, deleting,
creating, selecting) scenes on the backend via the client.

"""

import argparse
from util_client.post_json import post_json_string


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
    create_parser.add_argument('object_id', type=str, nargs='*',
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
    except:
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
        object_id = parsed_args.object_id
        object_id = clean_list(object_id)
        scenes_create(c_data, object_id=object_id)

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


def pretty_print_scene(scene_hash, scene, host, port):
    """
    Pretty print a scene.

    Print a scene (and the objects in it) to the screen.

    Args:
     scene_hash (str): The unique identifier of the scene.
     scene (dict): Contains all the information about the scene.
     host (str): The address of the backend server, for printing a URL.
     port (int): The port of the backend server, for printing a URL.

    Returns:
     None: Nothing.

    Todo:
     Maybe rework this to make it even prettier!

    """
    print()             # Newline

    if scene is None:
        print('Invalid scene: {}'.format(scene_hash))

    else:
        print('Scene {} can be found at'.format(scene_hash))
        print('  http://{}:{}/scenes/{}'. format(
            host, port, scene_hash))

        print('----------------------------------------' +
              '----------------------------------------')

        for entry in scene['object_list']:
            print('  {}'.format(entry))

            print('========================================' +
                  '========================================')

    return None


def scenes_list(c_data, just=None):
    """
    List one, several or all scenes.

    Args:
     c_data (dict): A dictionary containing host, port and headers.
     just (None or list, optional, defaults to None): A list of scene_hashes
      of a limited subset of the available scenes, we want to display.

    Returns:
     None: Nothing.

    """
    host = c_data['host']
    port = c_data['port']
    headers = c_data['headers']

    api_call = 'scenes_infos'
    data = None
    answer = post_json_string(
        api_call=api_call, data=data, connection_data=c_data)

    if answer == {}:
        # If there are no scenes to display on the server
        print('There are no scenes to display.')

    if just is None:
        # If we only want to list a limited amount of scenes
        for scene_hash in answer.keys():
            pretty_print_scene(scene_hash, answer.get(scene_hash), host, port)
    else:
        # List everything we have
        for scene_hash in just:
            pretty_print_scene(scene_hash, answer.get(scene_hash), host, port)

    return None


def scenes_create(c_data, object_id):
    """
    Create a new scene.

    If object_id is an empty list, an empty scene will be created. After
    creation a link to the new scene is printed to the screen.

    Args:
     c_data (dict): A dictionary containing host, port and headers.
     object_id (list): A list of objects to include on creation of a new scene.
      Valid object names can be found by typing 'objects'.

    Returns:
     None: Nothing.

    """
    host = c_data['host']
    port = c_data['port']
    headers = c_data['headers']

    api_call = 'scenes_create'
    data = {'object_path': object_id}
    response = post_json_string(
        api_call=api_call, data=data, connection_data=c_data)

    try:
        output = ('Created scene {}\n\n'.format(response['created']) +
                  'It can be found at http://{}:{}/scenes/{}'.format(
                      host, port, response['created']))
        print(output)
    except TypeError:
        print('Error: wrong id?')

    return None


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
