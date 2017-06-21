#!/usr/bin/env python3

"""
Terminal-like interface for interacting with calculix-clone.
"""

import cmd
import json
import argparse
import textwrap
import requests


AGENT = 'calculix_clone'
VERSION = '1-alpha'

def grab_CLA():
    """
    Parse the command line arguments.
    """

    parser = argparse.ArgumentParser()
    parser.add_argument('--host', type=str, default='localhost',
                        help='Host to connect to.')
    parser.add_argument('--port', type=int, default=8008,
                        help='Port of host.')
    parsed_args = parser.parse_args()

    return parsed_args


class Terminal(cmd.Cmd):
    """
    Send commands to the server.
    """

    def __init__(
            self,
            args
    ):
        """
        Init function for the terminal.
        """

        # Initialise the class defaults
        cmd.Cmd.__init__(self)

        # Set the program details
        self.prompt = '>> '
        self.intro = 'Welcome to {} command line interface version {}.'.format(AGENT, VERSION)
        self.headers = {'user-agent': '{}/{}'.format(AGENT, VERSION)}
        self.host = args.host
        self.port = args.port

        # Check if the host is running a compatible server
        if not self.target_compatible():
            warning_text = textwrap.wrap('The host does not appear to support what we would ' +
            'like him to do. Do not expect any functionality.')
            for line in warning_text:
                print(line)
            print()             # Newline

        return None


    def target_compatible(self):
        """
        Check whether or not we are dealing with a compatible server.
        """

        # Call the about page of the host
        response = self.post_json_string(api_call='connect_client')

        # Check if we see what we want to see
        expected_program_response = AGENT

        is_compatible = response['program'] == expected_program_response
        print('Host is compatible.')
        return is_compatible


    def post_json_string(
            self,
            api_call, data=''
    ):
        """
        Prototype for sending a post request with error handling and so on.
        """

        try:
            api_call = api_call
            url = 'http://{}:{}/api/{}'.format(self.host, self.port, api_call)
            response = requests.post(
                url=url,
                json=data,
                timeout=3.5,
                headers=self.headers
            )

            response.raise_for_status()
        except BaseException as e:
            return '{}'.format(e)

        return response.json()

    def do_scenes(self, line):
        """
        Handle scenes. For a more complete documentation type scenes -h
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
                                 help='If provided we only list the properties '+
                                 'of this/these scene/s.')

        create_parser = subparsers.add_parser(
            'create',
            help='Create an empty scene.'
        )

        delete_parser = subparsers.add_parser(
            'delete',
            help='Delete a scene.'
        )
        delete_parser.add_argument('scene_hash', type=str, nargs='+',
                                   help='The scene we want to delete. ' +
                                   'Requires the full SHA1 hash.')

        select_parser = subparsers.add_parser(
            'select',
            help='Select a scene.'
        )
        select_parser.add_argument('scene_hash', type=str,
                                   help='The scene we want to select. ' +
                                   'Requires the full SHA1 hash.')

        line_split = line.split(' ')

        try:
            # Parse the arguments.
            parsed_args = scenes.parse_args(line_split)
        except:
            # Something went wrong. argparse will tell us anyway so no need to
            # report anything here.
            return None

        scenes_action = parsed_args.scenes

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
                    return

                else:
                    # Make this pretty!
                    print(scene_hash)
                    print(scene)
                    return

            api_call = 'scenes_list'
            data = ''
            answer = self.post_json_string(api_call=api_call, data=data)

            # If there are no scenes to display on the server
            if answer == {}:
                print('There are no scenes to display.')

            # If we only want to list a limited amount of scenes
            if just == None:
                for scene_hash in answer.keys():
                    pretty_print_scene(scene_hash, answer.get(scene_hash))
            # List everything we have
            else:
                for scene_hash in just:
                    pretty_print_scene(scene_hash, answer.get(scene_hash))

            return None

        def scenes_create():
            """
            Create a new scene.
            """

            api_call = 'scenes_create'
            data = ''
            response = self.post_json_string(api_call=api_call, data=data)

            output = ('Created empty scene {}\n\n'.format(response['created']) +
                      'It can be found at http://{}:{}/scenes/{}'.format(
                          self.host, self.port, response['created']))
            print(output)

            return None

        def scenes_delete(scene_hash):
            """
            Delete a scene.
            """

            api_call = 'scenes_delete'
            data = {'scene_hash': scene_hash}
            self.post_json_string(api_call=api_call, data=data)

            return None

        def scenes_select():
            """
            Select a scene.
            """

            api_call = 'scenes_select'
            data = ''
            answer = self.post_json_string(api_call=api_call, data=data)

            return None

        # If we want to list the available scenes
        if scenes_action == 'list':
            just = parsed_args.just
            scenes_list(just=just)

        # If we want to create a new and empty scene
        elif scenes_action == 'create':
            scenes_create()

        # If we want to delete a scene
        elif scenes_action == 'delete':
            scene_hash = parsed_args.scene_hash
            scenes_delete(scene_hash)

        # If we want to select a scene to perform operations on it
        elif scenes_action == 'select':
            scene_hash = parsed_args.scene_hash
            scenes_select(scene_hash)

        return None

    def do_exit(self, line):
        """
        Exit the CLI.
        """
        print('Bye.')
        return -1

    def do_quit(self, line):
        """
        Exit alias.
        """
        return(self.do_exit(line))


if __name__ == '__main__':
    """
    Start.
    """
    ARGS = grab_CLA()
    CLI = Terminal(args=ARGS)
    CLI.cmdloop()


