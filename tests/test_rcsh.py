#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_rcsh
----------------------------------

Tests for `rcsh` module.
"""


import os, sys
import unittest

from rcsh import rcsh

HERE = os.path.dirname(__file__)
DATA_DIR = os.path.join(HERE, 'data')
TMP_DIR = os.path.join(HERE, 'tmp')

class TestRcsh(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_000_dummy(self):
        print(HERE, DATA_DIR, TMP_DIR)
        return 1

    def test_000_load_whitelists(self):
        exact_allowed, regex_allowed = rcsh.load_whitelists('testdummy', os.path.join(HERE, 'test-config', 'rcsh.d'))
        print(exact_allowed, regex_allowed)
        self.assertEqual(exact_allowed, ['uptime'])
        self.assertEqual(regex_allowed, ['^ls(?: -[lahtr]+)?$'])


if __name__ == "__main__":
    unittest.main()