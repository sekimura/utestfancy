#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import unittest
from StringIO import StringIO

# Path hack.
sys.path.insert(0, os.path.abspath('..'))

import utestfancy

class BasicFancyTestRunnerTest(unittest.TestCase):
    """ Basic test for FancyTestRunner
    """
    def test_stream(self):
        """ stream should be utestfancy.core._StylizeWriteInDecorator
        """
        runner = utestfancy.FancyTestRunner()
        self.assertTrue(isinstance(runner.stream,
                                   utestfancy.core._StylizeWritelnDecorator))

    def test_writeln(self):
        """ test writeln 'style' arg
        """
        stream_mock = StringIO()
        runner = utestfancy.FancyTestRunner(stream=stream_mock)

        runner.stream.writeln('foo')
        self.assertEqual(stream_mock.getvalue(), 'foo\n')
        stream_mock.seek(0)

        runner.stream.writeln('foo', style='bold')
        self.assertEqual(stream_mock.getvalue(), '\033[1mfoo\033[22m\n')
        stream_mock.seek(0)

        runner.stream.writeln('foo', style='bold:red')
        self.assertEqual(stream_mock.getvalue(),
                        '\033[31m\033[1mfoo\033[22m\033[39m\n')
        stream_mock.close()

if __name__ == '__main__':
    unittest.main()
