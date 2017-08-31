#!/usr/bin/env python3

import textwrap


def print_help(help_text):
    """
    A small helper function that prints out a help string in a nice format.

    Args:
     help_text (str): The 'unformated' help string.

    Returns:
     None: Nothing.

    Todo:
     I think this can be done waaay more elegant...

    """

    # Take out indentation
    dedented = textwrap.dedent(help_text)

    # Split the string in lines
    splitlines = dedented.splitlines()

    # Delete a leading and trailing newline
    if splitlines[0] == '':
        splitlines.pop(0)
    if splitlines[-1] == '':
        splitlines.pop(-1)

    # Construct the paragraphs
    paragraphs = ''
    for line in splitlines:
        if line == '':
            paragraphs += '\n'
        else:
            paragraphs += line + ' '

    # Split on newlines
    paragraphs = paragraphs.split('\n')

    # print()                 # Newline
    for paragraph in paragraphs:
        wrapped_string = textwrap.wrap(paragraph)
        for line in wrapped_string:
            print(line)
        # print()             # Newline after each paragraph

    return None
