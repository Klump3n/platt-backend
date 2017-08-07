#!/usr/bin/env python3
"""
Get the version number of the program.
"""

import subprocess

# Version template
version_dict = {
    'program': 'FemGL',
    'version': ''
}

def short_version_string():
    """
    Return the short version string.
    """

    version = subprocess.check_output(
        ['git', 'describe', '--tags', '--always'])

    return version.decode('utf-8').splitlines()[0]

def long_version_string():
    """
    Return the long version string.
    """

    version = subprocess.check_output(
        ['git', 'describe', '--long', '--tags', '--always'])

    return version.decode('utf-8').splitlines()[0]

def dirty_version_string():
    """
    Return the dirty version string.
    """

    version = subprocess.check_output(
        ['git', 'describe', '--long', '--dirty', '--tags', '--always'])

    return version.decode('utf-8').splitlines()[0]


def version(detail='dirty'):
    """
    Find the version number of the git repository.
    """

    # Specify which arguments are valid
    if detail not in ['short', 'long', 'dirty']:
        print('Argument \'detail\' must be either \'short\', \'long\' or '+
              '\'dirty\'. Setting to \'dirty\'')

    # Try to get a version number from git
    try:
        p = subprocess.run(
            ['git', 'describe'],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
        )

        # If we don't get a returncode of 0 we are probably not in any git repo
        if p.returncode != 0:
            # print('Not in any git repository.')
            version = 'NoVer'
        # Else, we are in a repo
        else:
            if detail == 'short':
                version = short_version_string()
            elif detail == 'long':
                version = long_version_string()
            else:
                version = dirty_version_string()

    # Maybe git is not installed or something else is happening
    except FileNotFoundError:
        # print('Git not found.')
        version = 'NoVer'

    version_dict['version'] = version

    return version_dict

