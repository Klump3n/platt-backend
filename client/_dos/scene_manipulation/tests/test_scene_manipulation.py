#!/usr/bin/env python3
"""
Tests for scene manipulation.

"""
import unittest
import unittest.mock as mock

import os
import sys
sys.path.append(os.path.join('..', '..', '..', '..'))
import client._dos.scene_manipulation.scene_manipulation as scene_manipulation


class Test_scene_manipulation(unittest.TestCase):
    """
    Testing the scene_manipulation module.

    """

    def setUp(self):
        """
        Set up the testing.

        """
        self.host = '0.0.0.0'
        self.port = 8008
        self.program_name = 'norderney'
        self.program_version = 'alpha-21-ge897462'

        self.headers = {'user-agent': '{}/{}'.format(
            self.program_name, self.program_version)}

        self.c_data = {}
        self.c_data['host'] = self.host
        self.c_data['port'] = self.port
        self.c_data['headers'] = self.headers

    def test_select(self):
        """Start a new cmd.Cmd instance for manipulating scenes

        """
        with mock.patch(
                'client._dos.scene_manipulation.scene_manipulation.SceneTerminal'
        ) as mock_scene_terminal:

            res = scene_manipulation.select(self.c_data, 'asd')
            mock_scene_terminal.assert_called_with(self.c_data, 'asd')

    def test_SceneTerminal(self):
        """Test the SceneTerminal class

        """
        pass

if __name__ == '__main__':
    unittest.main(verbosity=2)
