#!/usr/bin/env python3
"""
Contains a class that spawns a second terminal within the client terminal for
manipulating scenes.

"""
import re
import cmd

from client.util_client.send_http_request import send_http_request
from client.util_client.print_function_usage import print_help


class SceneTerminal(cmd.Cmd):
    """
    The terminal class for manipulating scenes.

    """
    def __init__(self, c_data, scene_hash):
        """
        Init function for the scene manipulation terminal.

        Args:
         c_data (dict): A dictionary containing host, port and headers.
         scene_hash (str): Unique identifier of the scene.

        Returns:
         None: Nothing.

        """
        if not isinstance(c_data, dict):
            raise TypeError('c_data is {}, expected dict'.format(
                type(c_data).__name__))

        if not isinstance(scene_hash, str):
            raise TypeError('scene_hash is {}, expected str'.format(
                type(scene_hash).__name__))

        # Initialise the class defaults
        cmd.Cmd.__init__(self)

        # Set the program details
        self.c_data = c_data
        self.scene_hash = scene_hash

        # For saving the names of the available fields
        self._nodal_fields = []
        self._elememtal_fields = []

        prompt_info = self.scene_hash[0:7]

        # prompt = """({}) >>
        # """.format(prompt_info)
        # self.prompt = textwrap.dedent(prompt)

        self.prompt = '({}) >> '.format(prompt_info)

        return None

    def cmdloop(self, intro=None):
        """
        Override cmd.Cmd.cmdloop so we catch Ctrl-C keyboard interrupts
        without exiting the program.

        Args:
         intro (str, defaults to None): The 'intro' message. This message will
          be displayed in a line before every new prompt.

        """
        while True:
            try:
                # Set the message we display on pressing Ctrl-C to an empty
                # string.
                # super references the parent class, i.e. cmd.Cmd
                super().cmdloop(intro="")
                self.postloop()
                break
            except KeyboardInterrupt:
                print('')

        return None

    def do_exit(self, line):
        """
        Print 'Bye' and exit the program.

        Args:
         line (str): The parsed line for the command line.

        Returns:
         int (-1): Return code for exiting the program.

        """
        return -1

    def help_exit(self):
        """
        Print the help message for 'exit'.

        """
        print("Leave scene {}".format(self.scene_hash))

    def do_quit(self, line):
        """
        Alias for exit.

        Args:
         line (str): The parsed line for the command line.

        Returns:
         int: -1, since exit returns -1.

        """
        return self.do_exit(line)

    def help_quit(self):
        """
        Print the help message for 'quit'.

        """
        self.help_exit()

    def do_list(self, line):
        """
        List the LOADED datasets of the scene.

        Args:
         line (str): The parsed line for the command line.

        """
        from client._dos.do_scenes import scenes_list  # Does not work at top
        # of file, circular import shennanigans.
        scene_hash = [self.scene_hash]
        scenes_list(self.c_data, just=scene_hash)

    def help_list(self):
        """
        Print the help message for 'list'.

        """
        help_text = """
        List the datasets of the scene.
        """

        print_help(help_text)

        return None

    def do_fields(self, line):
        """
        Get a list of fields or set the current field.

        Args:
         line (str): The parsed line for the command line.

        """
        line_args = line.split()

        if len(line_args) == 0:
            return None

        # if the first thing is not a hash
        if not re.search('^[0-9a-f]{40}$', line_args[0]):
            print('{} not a hash'.format(line_args[0]))

        else:
            api_endpoint = 'scenes/{}/{}/fields'.format(
                self.scene_hash, line_args[0])
            if len(line_args) == 1:
                response = send_http_request(
                    http_method='GET',
                    api_endpoint=api_endpoint,
                    connection_data=self.c_data,
                    data_to_transmit=None
                )

                if response is not None:
                    selected_field_name = (
                        response['datasetFieldSelected']['name'])
                    selected_field_type = (
                        response['datasetFieldSelected']['type'])

                    elemental_fields = (
                        response['datasetFieldList']['elemental'])
                    nodal_fields = response['datasetFieldList']['nodal']

                    if not (
                            selected_field_name in elemental_fields or
                            selected_field_name in nodal_fields
                    ):
                        print('Selected field: None')
                    else:
                        print('\nSelected field: {} field {}'.format(
                            selected_field_type, selected_field_name))

                    print('\nElemental fields:')
                    if len(elemental_fields) > 0:
                        for field in elemental_fields:
                            print('  {}'.format(field))
                    else:
                        print('  None')
                    print('\nNodal fields:')
                    if len(nodal_fields) > 0:
                        for field in nodal_fields:
                            print('  {}'.format(field))
                    else:
                        print('  None')
                    print('')

            # set none
            if (
                    len(line_args) == 3 and
                    line_args[1] == 'set' and
                    line_args[2] == 'none'
            ):
                data = {
                    'datasetFieldSelected': {
                        'type': '__no_type__',
                        'name': '__no_field__'
                    }
                }
                response = send_http_request(
                    http_method='PATCH',
                    api_endpoint=api_endpoint,
                    connection_data=self.c_data,
                    data_to_transmit=data
                )

                if response is not None:
                    if (
                            data['datasetFieldSelected'] ==
                            response['datasetFieldSelected']
                    ):
                        print('Unset fields')

            # set nodal or elemental
            if len(line_args) == 4:
                # [fields] __dataset_hash__ set nodal __field_id__
                if (
                        line_args[1] == 'set' and
                        (
                            line_args[2] == 'nodal' or
                            line_args[2] == 'elemental'
                        )
                ):
                    nod_elem = line_args[2]
                    field_name = line_args[3]
                    data = {
                        'datasetFieldSelected':
                        {
                            'type': line_args[2],
                            'name': line_args[3]
                        }
                    }
                    response = send_http_request(
                        http_method='PATCH',
                        api_endpoint=api_endpoint,
                        connection_data=self.c_data,
                        data_to_transmit=data
                    )

                    if response is not None:
                        # field could be set
                        if (
                                data['datasetFieldSelected'] ==
                                response['datasetFieldSelected']
                        ):
                            print('Set {} field {}'.format(
                                nod_elem, field_name))

                        # field could not be set
                        else:
                            print('Could not set {} field {}'.format(
                                nod_elem, field_name))

    def complete_fields(self, text, line, begidx, endidx):
        """
        Completion for dataset ids.

        If we try to get or set the fields in a scene, we need the
        dataset_hash. If we don't want to copy and paste these hashes it would
        be nice to have a form of auto completion. This functions solves that
        need.
        It also completes get/set, elemental/nodal/none and the available field
        names for either elemental or nodal fields.

        Args:
         text (str): The text we want to complete.
         line (str): The whole command line input.
         begidx (int): The position where text starts in line.
         endidx (int): The position where text ends in line.

        Returns:
         array: An array with options for auto completion.

        """
        line_args = line.split()

        if (
                (len(line_args) == 1 and line[-1] == ' ') or
                (len(line_args) == 2 and
                 not re.search('^[0-9a-f]{40}$', line_args[1]))
        ):
            datasets_in_scene = send_http_request(
                http_method='GET',
                api_endpoint='scenes/{}'.format(self.scene_hash),
                connection_data=self.c_data,
                data_to_transmit=None
            )

            if datasets_in_scene is None:
                return None

            loaded_datasets = [x['datasetHash'] for x
                               in datasets_in_scene['loadedDatasets']]

            mline = line.partition(' ')[2]
            offs = len(mline) - len(text)
            return [s[offs:] for s in loaded_datasets if s.startswith(mline)]

        # Options for things to do with the fields, like SET or GET
        options = [
            'get',
            'set'
        ]

        if (
                (re.search('^[0-9a-f]{40}$', line_args[1])) and
                (
                    (len(line_args) == 2 and line[-1] == ' ') or
                    (len(line_args) == 3 and line_args[2] not in options)
                )
        ):
            dataset_hash = re.search('^[0-9a-f]{40}$', line_args[1]).group(0)
            mline = line.partition('{} '.format(dataset_hash))[2]
            offs = len(mline) - len(text)
            return [s[offs:] for s in options if s.startswith(mline)]

        # Select if we want to set elemental or nodal fields
        elem_nod = [
            'elemental',
            'nodal',
            'none'
        ]

        if (
                (line_args[2] == 'set') and
                (
                    (len(line_args) == 3 and line[-1] == ' ') or
                    (len(line_args) == 4 and line_args[3] not in elem_nod)
                )
        ):
            # reset elemental and nodal fields
            self._nodal_fields = []
            self._elememtal_fields = []

            mline = line.partition('set ')[2]
            offs = len(mline) - len(text)
            return [s[offs:] for s in elem_nod if s.startswith(mline)]

        # Autocomplete nodal fields
        if (
                line_args[3] == 'nodal' and
                (
                    (len(line_args) == 4 and line[-1] == ' ') or
                    (len(line_args) == 5 and line_args[4] not
                     in self._nodal_fields)
                )
        ):
            api_endpoint = 'scenes/{}/{}/fields'.format(
                self.scene_hash, line_args[1])
            response = send_http_request(
                http_method='GET',
                api_endpoint=api_endpoint,
                connection_data=self.c_data,
                data_to_transmit=None
            )

            if response is not None:
                self._nodal_fields = response['datasetFieldList']['nodal']

                mline = line.partition('nodal ')[2]
                offs = len(mline) - len(text)
                return [s[offs:] for s in self._nodal_fields
                        if s.startswith(mline)]

        # Autocomplete elemental fields
        if (
                line_args[3] == 'elemental' and
                (
                    (len(line_args) == 4 and line[-1] == ' ') or
                    (len(line_args) == 5 and line_args[4] not
                     in self._elemental_fields)
                )
        ):
            api_endpoint = 'scenes/{}/{}/fields'.format(
                self.scene_hash, line_args[1])
            response = send_http_request(
                http_method='GET',
                api_endpoint=api_endpoint,
                connection_data=self.c_data,
                data_to_transmit=None
            )

            if response is not None:
                self._elemental_fields = (
                    response['datasetFieldList']['elemental'])

                mline = line.partition('elemental ')[2]
                offs = len(mline) - len(text)
                return [s[offs:] for s in self._elemental_fields
                        if s.startswith(mline)]

    def help_fields(self):
        """
        Print the help message for 'fields'.

        """
        help_text = """
        Get information about the available and set fields or set a field for a
        dataset.

        Use cases:
        fields 1ed75019714252d45effb9b5d0408a2f4f31da7a

        Returns the set field and the available fields for the dataset hash
        1ed75019714252d45effb9b5d0408a2f4f31da7a.


        fields 1ed75019714252d45effb9b5d0408a2f4f31da7a set nodal nt11

        Sets the field for the dataset hash
        1ed75019714252d45effb9b5d0408a2f4f31da7a to the nodal field nt11.


        fields 1ed75019714252d45effb9b5d0408a2f4f31da7a set none

        Unsets the field for the dataset hash
        1ed75019714252d45effb9b5d0408a2f4f31da7a.
        """

        print_help(help_text)

        return None


def select(c_data, scene_hash):
    """
    Select a single scene.

    This assumes that the provided scene_hash refers to a scene that exists.

    Args:
     c_data (dict): A dictionary containing host, port and headers.
     scene_hash (str): The scene_hash we want to select.

    Returns:
     None: Nothing.

    """
    if not isinstance(scene_hash, str):
        raise TypeError('scene_hash is {}, expected str'.format(
            type(scene_hash).__name__))

    scene_terminal = SceneTerminal(c_data, scene_hash)
    scene_terminal.cmdloop()
