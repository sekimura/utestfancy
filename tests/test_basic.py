#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import unittest

# Path hack.
sys.path.insert(0, os.path.abspath('..'))

from utestfancy import FancyTestRunner

class BarTestCase(unittest.TestCase):
    """ Sample Test Case
    """
    def setUp(self):
        self.foo = 'bar'

    def test_bar(self):
        "self.foo is bar"
        self.assertEqual(self.foo, 'bar')


if __name__ == '__main__':
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(BarTestCase))
    FancyTestRunner(verbosity=2).run(suite)
