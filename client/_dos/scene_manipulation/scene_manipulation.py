#!/usr/bin/env python3
"""
Contains a class that spawns a second terminal within the client terminal for
manipulating scenes.

"""
import cmd
import textwrap
import argparse


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
        self.scene_hash = scene_hash

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
                super().cmdloop(intro="")  # super references the parent class, i.e. cmd.Cmd
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
