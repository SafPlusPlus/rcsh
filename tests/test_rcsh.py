#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_rcsh
----------------------------------

Tests for `rcsh` module.
"""

import os, sys, unittest
from rcsh import rcsh

HERE = os.path.dirname(__file__)

class TestRcsh(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_000_load_config(self):
        config = rcsh.get_configuration(os.path.join(HERE, 'test-config', 'rcsh'))
        self.assertEqual(config.get('DEFAULT', 'filter_dir'), '/etc/rcsh.d')
        self.assertEqual(config.getint('DEFAULT', 'timeout'), 30)

    def test_001_load_whitelists(self):
        exact_allowed, regex_allowed = rcsh.load_whitelists('testdummy', os.path.join(HERE, 'test-config', 'rcsh.d'))
        self.assertEqual(exact_allowed, ['uptime'])
        self.assertEqual(regex_allowed, ['^ls(?: -[lahtr]+)?$'])

    def test_002_filter(self):
        exact_allowed = ['validcommand']
        regex_allowed = ['^ls(?: -[lahtr]+)?$']
        self.assertTrue(rcsh.is_invocation_allowed('validcommand', exact_allowed, regex_allowed))
        self.assertTrue(rcsh.is_invocation_allowed('ls -ltr', exact_allowed, regex_allowed))
        self.assertFalse(rcsh.is_invocation_allowed('sudo reboot', exact_allowed, regex_allowed))



if __name__ == "__main__":
    unittest.main()