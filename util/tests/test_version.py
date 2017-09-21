#!/usr/bin/env python3
"""
Testing the version printing function

"""
import unittest
from unittest import mock
import subprocess

# Append the parent directory for importing the file.
import os
import sys
sys.path.append(os.path.join('..', '..'))  # Append the program root dir
import util.version


class Test_version(unittest.TestCase):
    """
    Unittest for version.
    """
    def setUp(self):
        """Setup the test case

        """
        self.git_running = mock.MagicMock(subprocess.CompletedProcess)
        self.git_running.args = []  # Just init, not used
        self.git_running.returncode = 0

        self.not_in_repo = mock.MagicMock(subprocess.CompletedProcess)
        self.not_in_repo.args = []  # Just init, not used
        self.not_in_repo.returncode = 128

        self.program_name = 'norderney'
        self.version_string = 'a_version_string'
        self.version_string_no_ver = 'a_version_string_no_version'

        self.expected_version_dict = {
            'programName': self.program_name,
            'programVersion': self.version_string
        }

        self.expected_version_dict_no_version = {
            'programName': self.program_name,
            'programVersion': self.version_string_no_ver
        }

    def test_version_dirty(self):
        """Return a dirty version string

        """
        return_dirty_describe = b'a_version_string\n'
        expected_return = self.version_string
        with mock.patch(
                'util.version.subprocess.check_output',
                spec=subprocess.check_output,
                return_value=return_dirty_describe
        ) as describe:
            res = util.version.dirty_version_string()
            describe.assert_called_with(
                ['git', 'describe', '--long', '--dirty', '--tags', '--always'])
            self.assertEqual(res, expected_return)

    def test_version_long(self):
        """Return a long version string

        """
        return_dirty_describe = b'a_version_string\n'
        expected_return = self.version_string
        with mock.patch(
                'util.version.subprocess.check_output',
                spec=subprocess.check_output,
                return_value=return_dirty_describe
        ) as describe:
            res = util.version.long_version_string()
            describe.assert_called_with(
                ['git', 'describe', '--long', '--tags', '--always'])
            self.assertEqual(res, expected_return)

    def test_version_short(self):
        """Return a short version string

        """
        return_dirty_describe = b'a_version_string\n'
        expected_return = self.version_string
        with mock.patch(
                'util.version.subprocess.check_output',
                spec=subprocess.check_output,
                return_value=return_dirty_describe
        ) as describe:
            res = util.version.short_version_string()
            describe.assert_called_with(
                ['git', 'describe', '--tags', '--always', '--abbrev=0'])
            self.assertEqual(res, expected_return)

    def test_try_version_from_file(self):
        """Read a backup version string from file

        """
        # Reads a string from file
        with mock.patch(
                'builtins.open',
                mock.mock_open(read_data=self.version_string)
        ) as backup_file:
            res = util.version.try_version_from_file()
            self.assertEqual(res, self.version_string)
            backup_file.assert_called()

        # A backup file could not be found
        with mock.patch(
                'builtins.open',
                side_effect=FileNotFoundError
        ) as backup_file:
            res = util.version.try_version_from_file()
            self.assertEqual(res, 'NoVer')
            backup_file.assert_called()

    def test_version_invalid_argument(self):
        """Call version with invalid argument

        """
        # Return None if an invalid argument is supplied
        returned_value = util.version.version('invalid_string')
        self.assertIsNone(returned_value)

    def test_version(self):
        """Return version with git working and in repository

        """
        # git is up and running, so we write our string to a (mock) file
        with mock.patch('subprocess.run', return_value=self.git_running) as running_git:
            with mock.patch(
                    'util.version.dirty_version_string', spec=util.version.dirty_version_string,
                    return_value=self.version_string) as describe:
                with mock.patch('builtins.open', mock.mock_open()) as mock_open:
                    res = util.version.version()
                    describe.assert_called_with()
                    running_git.assert_called_with(
                        ['git', 'describe'],
                        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
                    )
                    mock_open.assert_called()
                    self.assertEqual(res, self.expected_version_dict)

        # git is up and running, call with 'detail' parameter
        pairs = {
                'short': 'util.version.short_version_string',
                'long': 'util.version.long_version_string',
                'dirty': 'util.version.dirty_version_string'
        }
        for call in pairs:
            with mock.patch('subprocess.run', return_value=self.git_running) as running_git:
                with mock.patch(
                        pairs[call], autospec=True,
                        return_value=self.version_string) as describe:

                    res = util.version.version(call)
                    describe.assert_called_with()
                    running_git.assert_called_with(
                        ['git', 'describe'],
                        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
                    )
                    self.assertEqual(res, self.expected_version_dict)

    def test_version_no_repo(self):
        """Call version outside of a git repo

        """
        # No repository but backup file
        with mock.patch(
                'subprocess.run', return_value=self.not_in_repo
        ) as no_repo:
            with mock.patch(
                    'util.version.try_version_from_file', return_value=self.version_string
            ) as version_file_string:

                # Check that a warning was raised
                with self.assertWarns(UserWarning):
                    res = util.version.version()

                res = util.version.version()
                no_repo.assert_called()
                version_file_string.assert_called()

                self.assertEqual(res, self.expected_version_dict)


        # No repository AND no backup file
        with mock.patch('subprocess.run', return_value=self.not_in_repo) as no_repo:
            with mock.patch(
                    'util.version.try_version_from_file', return_value=self.version_string_no_ver
            ) as version_file_string:

                # Check that a warning was raised
                with self.assertWarns(UserWarning):
                    res = util.version.version()

                res = util.version.version()
                no_repo.assert_called()
                version_file_string.assert_called()

                self.assertEqual(res, self.expected_version_dict_no_version)


if __name__ == '__main__':
    unittest.main(verbosity=2)
