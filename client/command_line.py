#!/usr/bin/env python3
"""
Terminal-like interface for interacting with calculix-clone.
"""

import cmd
import sys
import argparse

# Command line interface functionality
from _dos.do_scenes import scenes
from _dos.do_objects import objects

# Some utility functions
from util.post_json import post_json_string
from util.test_host import target_online_and_compatible

# Get the version from the parent directory
sys.path.append('..')
from util.version import version


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

        # Version of the package
        self.version_dict = version(detail='long')
        program_name = self.version_dict['program']
        version_number = self.version_dict['version']

        # Initialise the class defaults
        cmd.Cmd.__init__(self)

        # Set the program details
        self.prompt = '>> '
        self.intro = (
            'Welcome to {} command line interface version {}.\n'\
            'To leave type \'exit\' or \'quit\'.'.format(
                program_name, version_number))
        self.headers = {'user-agent': '{}/{}'.format(
            program_name, version_number)}
        self.host = args.host
        self.port = args.port

        # A dict with connection data for easy handing into functions
        self.c_data = {}
        self.c_data['host'] = self.host
        self.c_data['port'] = self.port
        self.c_data['headers'] = self.headers

        # Check if the host is running a compatible server
        if not target_online_and_compatible(self.c_data, self.version_dict):
            sys.exit('Exiting.')

        return None

    def cmdloop(self, intro=None):
        """
        A slightly modified version of the cmdloop that catches Ctrl-C keyboard
        interrupts.
        """

        print(self.intro)

        while True:
            try:
                super().cmdloop(intro="")  # super references the parent class, i.e. cmd.Cmd
                self.postloop()
                break
            except KeyboardInterrupt:
                print('')

    def do_objects(self, line):
        """
        List all the available simulation data directories.
        """
        return objects(self.c_data)

    def do_scenes(self, line):
        """
        Handle scenes. For a more complete documentation type scenes -h
        """
        return scenes(line, self.c_data)

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


