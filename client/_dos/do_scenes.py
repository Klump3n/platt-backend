#!/usr/bin/env python3
"""
Do scenes for CLI.
"""

import argparse
from util.post_json import post_json_string

def scenes(line, c_data):
    """
    The do_scenes routine for the CLI.
    """

    host = c_data['host']
    port = c_data['port']
    headers = c_data['headers']

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
                             help='If provided we only list the properties '+
                             'of this/these scene/s.')

    create_parser = subparsers.add_parser(
        'create',
        help='Create an empty scene.'
    )
    create_parser.add_argument('object_id', type=str, nargs='*',
                               help='The id of the object we want to ' +
                               'instantiate the scene with. Valid '+
                               'identifiers are available via the command '+
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
        return None

    scenes_action = parsed_args.scenes

    def clean_list(dirty_list):
        """
        This is a small helper function that removes empty entries
        from a list and casts everything to string.
        """

        list_length = len(dirty_list)

        for it in range(list_length):
            # Pop all empty entries
            try:
                empty_index = dirty_list.index('')
                dirty_list.pop(empty_index)
            except ValueError:
                continue

        for it, entry in enumerate(dirty_list):
            # Cast to string and remove all '-marks
            dirty_list[it] = str(dirty_list[it])
            dirty_list[it] = dirty_list[it].translate(
                {ord(c): None for c in '\''})

        return dirty_list

    #
    # Function definitions for the valid actions on scenes.
    def scenes_list(just=None):
        """
        List one, several or all scenes.
        """

        def pretty_print_scene(scene_hash, scene):
            """
            Pretty print a scene.
            """

            print()             # Newline

            if scene is None:
                print('Invalid scene: {}'.format(scene_hash))

            else:
                # Make this pretty!
                print('Scene {} can be found at'.format(scene_hash))
                print('  http://{}:{}/scenes/{}'. format(
                    host, port, scene_hash))

                print('----------------------------------------' +
                      '----------------------------------------')

                for entry in scene['object_list']:
                    print('  {}'.format(entry))

                print('========================================' +
                      '========================================')

            return

        api_call = 'scenes_infos'
        data = ''
        answer = post_json_string(
            api_call=api_call, data=data, connection_data=c_data)

        if answer == {}:
            # If there are no scenes to display on the server
            print('There are no scenes to display.')

        if just == None:
            # If we only want to list a limited amount of scenes
            for scene_hash in answer.keys():
                pretty_print_scene(scene_hash, answer.get(scene_hash))
        else:
            # List everything we have
            for scene_hash in just:
                pretty_print_scene(scene_hash, answer.get(scene_hash))

        return None

    def scenes_create(object_id):
        """
        Create a new scene.
        """

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

    def scenes_delete(scene_hash):
        """
        Delete a scene.
        """

        api_call = 'scenes_delete'
        # data = {'scene_hash': scene_hash}
        # self.post_json_string(api_call=api_call, data=data)
        for scene in scene_hash:
            data = {'scene_hash': scene}
            post_json_string(
                api_call=api_call, data=data, connection_data=c_data)

        return None

    def scenes_select():
        """
        Select a scene.
        """

        api_call = 'scenes_select'
        data = ''
        answer = post_json_string(
            api_call=api_call, data=data, connection_data=c_data)

        return None

    # If we want to list the available scenes
    if scenes_action == 'list':
        just = parsed_args.just
        if just is not None:
            just = clean_list(just)
        scenes_list(just=just)

    # If we want to create a new and empty scene
    elif scenes_action == 'create':
        object_id =  parsed_args.object_id
        object_id = clean_list(object_id)
        scenes_create(object_id=object_id)

    # If we want to delete a scene
    elif scenes_action == 'delete':
        scene_hash = parsed_args.scene_hash
        scene_hash = clean_list(scene_hash)
        scenes_delete(scene_hash)

    # If we want to select a scene to perform operations on it
    elif scenes_action == 'select':
        scene_hash = parsed_args.scene_hash
        scenes_select(scene_hash)

    return None
