#!/usr/bin/env python3
"""
Get the version number of the program.
"""

import subprocess
from warnings import warn


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

        # If we don't get a returncode of 0 we are probably not in any git repo.
        # Maybe someone has taken all the files out of the repo and uses them
        # without git..? Or maybe we are on windows?
        if p.returncode != 0:

            # Let's see if we can find a _version.py-file!
            try:
                with open('_version.py', 'r') as version_file:
                    version = version_file.readline().splitlines()[0]

                warning_message = ('We are probably not in a git repository. '\
                                   'Falling back to reading the version '\
                                   'string from file.')
                warn(warning_message)

            # Well, then just assign the NoVer version
            except FileNotFoundError:
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

        # Let's see if we can find a _version.py-file!
        try:
            with open('_version.py', 'r') as version_file:
                version = version_file.readline().splitlines()[0]

            warning_message = ('It seems that git is not installed. Falling '\
                               'back to reading the version string from file.')
            warn(warning_message)

        # Well, then just assign the NoVer version
        except FileNotFoundError:
            version = 'NoVer'

    # Write the version string to file for fallback use.
    with open('_version.py', 'w') as version_file:
        version_file.write('{}'.format(version))

    version_dict['version'] = version
    return version_dict
