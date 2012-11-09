#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import unittest
from StringIO import StringIO

# Path hack.
sys.path.insert(0, os.path.abspath('..'))

import utestfancy


class FooTestCase(unittest.TestCase):
    def runTest(self):
        self.assertEqual(1, 1)


class BasicFancyTestResultTest(unittest.TestCase):
    """ Basic test for FancyTestResult
    """
    def test_verbosity1(self):
        """ test with verbosity=1
        """
        out = StringIO()
        stream = utestfancy.core._StylizeWritelnDecorator(stream=out)
        descriptions = 1
        verbosity = 1
        result = utestfancy.core.FancyTestResult(stream, descriptions, verbosity)

        test = FooTestCase()
        result.addSuccess(test)
        green_dot = utestfancy.core._StylizeWritelnDecorator.stylize(
            '.', style='green')
        self.assertEqual(stream.getvalue(), green_dot)
        out.seek(0)

        result.addError(test, sys.exc_info())
        yellow_e = utestfancy.core._StylizeWritelnDecorator.stylize(
            'E', style='yellow')
        self.assertEqual(stream.getvalue(), yellow_e)
        out.seek(0)

        result.addFailure(test, sys.exc_info())
        red_f = utestfancy.core._StylizeWritelnDecorator.stylize(
            'F', style='red')
        self.assertEqual(stream.getvalue(), red_f)
        out.seek(0)

    def test_verbosity2(self):
        """ test with verbosity=2
        """
        out = StringIO()
        stream = utestfancy.core._StylizeWritelnDecorator(stream=out)
        descriptions = 1
        verbosity = 2
        result = utestfancy.core.FancyTestResult(stream, descriptions, verbosity)

        test = FooTestCase()
        result.addSuccess(test)
        stylize = utestfancy.core._StylizeWritelnDecorator.stylize
        success = '%s%s\n' % (
            stylize('  %s' % result.check_mark, style='green:bold'),
            ' %s' % result.getDescription(test)
        )
        self.assertEqual(stream.getvalue(), success)
        out.seek(0)

        result.addError(test, sys.exc_info())
        stylize = utestfancy.core._StylizeWritelnDecorator.stylize
        success = '%s%s\n' % (
            stylize('  %s' % result.ballot_x, style='yellow:bold'),
            stylize(' %s' % result.getDescription(test), style='yellow')
        )
        self.assertEqual(stream.getvalue(), success)
        out.seek(0)

        result.addFailure(test, sys.exc_info())
        stylize = utestfancy.core._StylizeWritelnDecorator.stylize
        success = '%s%s\n' % (
            stylize('  %s' % result.ballot_x, style='red:bold'),
            stylize(' %s' % result.getDescription(test), style='red')
        )
        self.assertEqual(stream.getvalue(), success)
        out.seek(0)

if __name__ == '__main__':
    unittest.main()
