#!/usr/bin/env python3
"""
Set the name of the program and implement methods to determine and display a
version identifier.

In the dict `VERSION_DICT` we set the name of the program.

"""

import subprocess
from warnings import warn

# Version template. The programs name is defined here. version will be
# overwritten by the functions in this module.
VERSION_DICT = {
    'program': 'norderney',
    'version': ''
}


def short_version_string():
    """
    Return the short version string.

    This contains the tag. If there have been commits since introduction of
    the tag it also includes the number of commits since introduction of the
    tag, as well as a short version of the commits SHA1 sum.

    Args:
     None: No parameters.

    Returns:
     str: The shortest possible unique version string.

    """

    version = subprocess.check_output(
        ['git', 'describe', '--tags', '--always'])

    return version.decode('utf-8').splitlines()[0]


def long_version_string():
    """
    Return the long version string.

    This contains the tag and the number of commits since introduction of the
    tag, as well as a short version of the commits SHA1 sum.

    Args:
     None: No parameters.

    Returns:
     str: A unique version string.

    """

    version = subprocess.check_output(
        ['git', 'describe', '--long', '--tags', '--always'])

    return version.decode('utf-8').splitlines()[0]


def dirty_version_string():
    """
    Return the dirty version string.

    This contains the tag and the number of commits since introduction of the
    tag, as well as a short version of the commits SHA1 sum. If there have been
    changes to the repository that have not been committed, a '-dirty' will be
    appended to the version string.

    Args:
     None: No parameters.

    Returns:
     str: A unique version string with hints on whether or not someone has
     tampered with the repository.

    """

    version = subprocess.check_output(
        ['git', 'describe', '--long', '--dirty', '--tags', '--always'])

    return version.decode('utf-8').splitlines()[0]


def version(detail='dirty'):
    """
    Find the version number of the git repository.

    Try to determine the version via 'git describe'. If this succeeds write the
    program name and version to a file. If the script is not able to determine
    the version, maybe because git is not installed or because the code has
    been removed from the (a) git-repository, it first tries to read the
    version number from a file. If that fails the version 'NoVer' will be
    assigned.

    Args:
     detail (str, ['short', 'long', 'dirty'], defaults to 'dirty'): How
      detailed would you like the version string. See the other functions in
      this module for further information.

    Returns:
     dict: The `VERSION_DICT`, containing the programs name and version.

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

    VERSION_DICT['version'] = version
    return VERSION_DICT
