#!/usr/bin/env python3
"""
Tests for the timestamp_to_sha1 function.

"""
import unittest

# Append the parent directory for importing the file.
import sys
import os
sys.path.append(os.path.join('..', '..', '..'))  # Append the program root dir
from backend.util.timestamp_to_sha1 import timestamp_to_sha1


class Test_Timestamps(unittest.TestCase):
    """
    Test class for timestamps.

    """

    def test_is_sha1_format(self):
        """SHA1 is actually 40 hex chars

        Regex this: '^[0-9a-f]{40}$'

        ^        Start Of String Anchor
        [0-9a-f] Any of the following characters: 0123456789abcdef
        {40}     Repeated 40 times
        $        End Of String Anchor

        Adapted from https://stackoverflow.com/questions/2982059/testing-if-string-is-sha1-in-php

        """
        sha1_string = timestamp_to_sha1()
        self.assertRegex(sha1_string, '^[0-9a-f]{40}$')

    def test_race_condition_not_equal(self):
        """Two SHA1 sums created in quick succession are unrelated

        This test is kind of wonky and I really have no idea of how to test
        this. At some point this function will be executed very successively
        and very quickly, so I do at least want to have tried... ¯\_(ツ)_/¯

        """
        first = timestamp_to_sha1()
        second = timestamp_to_sha1()
        self.assertNotEqual(first, second)

if __name__ == '__main__':
    """
    Testing as standalone program.

    """
    unittest.main(verbosity=2)
