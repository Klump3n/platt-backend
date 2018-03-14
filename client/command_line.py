#!/usr/bin/env python3
"""
Terminal-like interface for interacting with the backend.

"""
import cmd
import sys
import argparse
import textwrap

# Command line interface functionality
from _dos.do_scenes import scenes, scenes_help
from _dos.do_datasets import datasets, datasets_help

# Some utility functions
from client.util_client.send_http_request import send_http_request
from util_client.host_test import target_online_and_compatible

# # Get the version from the parent directory
sys.path.append('..')
import util.version


def parse_commandline():
    """
    Parse the command line arguments.

    Args:
     None: No parameters.

    Returns:
     namespace: A namespace containing all the parsed command line arguments.

    Notes:
     This function implements the defaults for the client program. The
     returned parameters and corresponding defaults are:

     --host  defaults to `localhost`
     --port  defaults to `8008`

    """
    parser = argparse.ArgumentParser(
        description=__doc__
    )
    parser.add_argument('--host', type=str, default='localhost',
                        help='Host to connect to.')
    parser.add_argument('--port', type=int, default=8008,
                        help='Port of host.')
    parsed_args = parser.parse_args()

    return parsed_args


class Terminal(cmd.Cmd):
    """
    Send commands to the backend api.

    This terminal-like interface sends commands to a running backend to change
    parameters, add data, etc. The address and port of this server are
    specified when Terminal is instantiated.

    For every do_* function we also implement a help_* function, that overrides
    the docstring for the do_* function. This is so we can clearly separate the
    documentation of the client from the documentation of how to use the
    program.

    """
    def __init__(
            self,
            host, port
    ):
        """
        Init function for the terminal.

        Display the version on starting the program. Set a command prompt and a
        user agent. Then check if the target server backend is actually online
        and is also running the same version. If that is not the case terminate
        the client program.

        Args:
         host (str): The IP of the target server backend.
         port (int): The port of the target, to which we are trying to connect.

        Returns:
         None: Nothing.

        """
        # Version of the package. Use the long version since nothing is gained
        # from dirty here. Later we might even go for short...?
        self.version_dict = util.version.version(detail='long')
        program_name = self.version_dict['programName']
        version_number = self.version_dict['programVersion']

        # Initialise the class defaults
        cmd.Cmd.__init__(self)

        # Set the program details
        # prompt = """>>
        # """
        # self.prompt = textwrap.dedent(prompt)

        self.prompt = '>> '
        self.intro = (
            'Welcome to {} command line interface version {}.\n'
            'To leave type \'exit\' or \'quit\'.'.format(
                program_name, version_number))
        # Construct the header
        self.headers = {'user-agent': '{}/{}'.format(
            program_name, version_number)}
        self.host = host
        self.port = port

        # A dict with connection data for easy handing into functions
        self.c_data = {}
        self.c_data['host'] = self.host
        self.c_data['port'] = self.port
        self.c_data['headers'] = self.headers

        # Check if the host is running a compatible server
        if not target_online_and_compatible(self.c_data):
            sys.exit('Exiting.')

        return None

    def cmdloop(self, intro=None):
        """
        Override cmd.Cmd.cmdloop so we catch Ctrl-C keyboard interrupts
        without exiting the program.

        Args:
         intro (str, defaults to None): The 'intro' message. This message will
          be displayed in a line before every new prompt.

        """

        print(self.intro)

        while True:
            try:
                # Set the message we display on pressing Ctrl-C to an empty
                # string.
                super().cmdloop(intro="")  # super references the parent class, i.e. cmd.Cmd
                self.postloop()
                break
            except KeyboardInterrupt:
                print('')

        return None

    def do_datasets(self, line):
        """
        Calls the imported datasets function and returns the result.

        See ``_dos.do_datasets.datasets`` for full documentation.

        Args:
         line (str): The parsed line from the command line.

        Returns:
         str: A formatted string containing all the datasets available.

        """
        datasets(self.c_data)

    def help_datasets(self):
        """
        Print help string for 'datasets'.

        """
        datasets_help()

    def do_scenes(self, line):
        """
        Calls the imported scenes function and returns the result.

        See ``_dos.do_scenes.scenes`` for full documentation.

        Args:
         line (str): The parsed line from the command line.

        Returns:
         str: A formatted string containing the returned information about the
          scenes.

        """
        scenes(line, self.c_data)

    def complete_scenes(self, text, line, begidx, endidx):
        """
        Completion for scenes.

        """
        options = [
            'list',
            'create',
            'delete',
            'select'
        ]

        line_args = line.split()

        if (
                ((len(line_args) == 1) and line[-1] == ' ') or
                ((len(line_args) == 2) and line_args[1] not in options)
        ):
            mline = line.partition('scenes ')[2]
            offs = len(mline) - len(text)
            return [s[offs:] for s in options if s.startswith(mline)]

        if (
                (
                    (line_args[1] == 'select') or
                    (line_args[1] == 'delete')
                ) and (
                    ((len(line_args) == 2) and line[-1] == ' ') or
                    (len(line_args) == 3)
                )
        ):
            # Maybe later do this less often
            response = send_http_request(
                http_method='GET',
                api_endpoint='scenes',
                connection_data=self.c_data,
                data_to_transmit=None
            )

            if response is None:
                return None

            # Extract activeScenes
            active_scenes = response['activeScenes']

            mline = line.partition('scenes {} '.format(line_args[1]))[2]
            offs = len(mline) - len(text)
            return [s[offs:] for s in active_scenes if s.startswith(mline)]

        if (
                (line_args[1] == 'create') and (
                    ((len(line_args) == 2) and line[-1] == ' ') or
                    (len(line_args) > 2)
                )
        ):
            response = send_http_request(
                http_method='GET',
                api_endpoint='datasets',
                connection_data=self.c_data,
                data_to_transmit=None
            )

            if response is None:
                return None

            # availableDatasets
            available_datasets = response['availableDatasets']

            # finds the last space in the line string
            last_space_in_line = line[::-1].find(' ')

            mline = line.partition(str(line[0:len(line) - last_space_in_line]))[2]
            offs = len(mline) - len(text)
            return [s[offs:] for s in available_datasets if s.startswith(mline)]


    def help_scenes(self):
        """
        Print the usage message for scenes.

        """
        scenes_help(self.c_data)

    def do_exit(self, line):
        """
        Print 'Bye' and exit the program.

        Args:
         line (str): The parsed line for the command line.

        Returns:
         int (-1): Return code for exiting the program.

        """
        print('Bye.')
        return -1

    def help_exit(self):
        """
        Print the help message for 'exit'.

        """
        print("Exit the command line interface.")

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


if __name__ == '__main__':
    """
    Start the client.
    """

    ARGS = parse_commandline()

    HOST = ARGS.host
    PORT = ARGS.port

    CLI = Terminal(host=HOST, port=PORT)
    CLI.cmdloop()
