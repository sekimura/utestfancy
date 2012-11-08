# -*- coding: utf-8 -*-
import time
import sys
import unittest


class _StylizeWritelnDecorator:
    """Used to decorate file-like objects with a handy 'writeln' method"""
    def __init__(self, stream):
        self.stream = stream

    def __getattr__(self, attr):
        return getattr(self.stream, attr)

    @classmethod
    def stylize(cls, text, style=''):
        styles = style.split(':')
        style_map = {
            'bold':      [1,  22],
            'italic':    [3,  23],
            'underline': [4,  24],
            'cyan':      [96, 39],
            'yellow':    [33, 39],
            'green':     [32, 39],
            'red':       [31, 39],
            'grey':      [90, 39],
            'green-hi':  [92, 32],
        }
        stash = [[], []]
        for style in styles:
            stash[0].append('\033[%sm' % style_map[style][0])
            stash[1].append('\033[%sm' % style_map[style][1])
        return ''.join(stash[0]) + text + ''.join(stash[1])

    def write(self, arg=None, style=None):
        writer = getattr(self.stream, 'write')
        if arg:
            if style:
                arg = self.stylize(arg, style)
        return writer(arg)

    def writeln(self, arg=None, style=None):
        if arg:
            if style:
                arg = self.stylize(arg, style)
            self.write(arg)
        # text-mode streams translate to \r\n if needed
        self.write('\n')


class _FancyTestResult(unittest.TestResult):
    """A test result class that can print formatted text results to a stream
    with fancy colors and unicode characters.

    Used by FancyTestRunner.
    """
    encoding = 'utf-8'
    # CHECK_MARK '✓' (U+2713)
    check_mark = u'✓'.encode(encoding)
    # BALLOT_X '✗' (U+2717)
    ballot_x = u'✗'.encode(encoding)
    # WHITE DIAMOND SUIT '♢' (U+2662)
    white_diamond_suit = u'♢'.encode(encoding)

    def __init__(self, stream, descriptions, verbosity):
        super(_FancyTestResult, self).__init__()
        self.successes = []
        self.stream = stream
        self.showAll = verbosity > 1
        self.dots = verbosity == 1
        self.descriptions = descriptions
        self._last_class_desc = None

    def getDescription(self, test):
        if self.descriptions:
            return test.shortDescription() or str(test)
        else:
            return str(test)

    def getShortTestCaseClassDescription(self, test):
        cls = test.__class__
        doc = cls.__doc__
        if doc:
            return doc.split("\n")[0].strip()
        else:
            return "%s.%s" % (cls.__module__, cls.__name__)

    def startTest(self, test):
        super(_FancyTestResult, self).startTest(test)
        if self.showAll:
            desc = self.getShortTestCaseClassDescription(test)
            if self._last_class_desc != desc:
                self.stream.writeln()
                self.stream.writeln('%s %s' % (
                    self.white_diamond_suit, desc), style='bold')
                self.stream.writeln()
                self._last_class_desc = desc

    def addSuccess(self, test):
        super(_FancyTestResult, self).addSuccess(test)
        if self.showAll:
            self.stream.write('  %s' % self.check_mark, style='green:bold')
            self.stream.writeln(' %s' % self.getDescription(test))
        elif self.dots:
            self.stream.write('.', style='green')
            self.stream.flush()

    def addFailure(self, test, err):
        super(_FancyTestResult, self).addFailure(test, err)
        if self.showAll:
            self.stream.write('  %s' % self.ballot_x, style='red:bold')
            self.stream.writeln(' %s' % self.getDescription(test), style='red')
        elif self.dots:
            self.stream.write('F', style='red')
            self.stream.flush()

    def printErrors(self):
        if self.failures or self.errors:
            self.stream.writeln()
        error = _StylizeWritelnDecorator.stylize('ERROR', style='yellow')
        self.printErrorList(error, self.errors)
        fail = _StylizeWritelnDecorator.stylize('FAIL', style='red')
        self.printErrorList(fail, self.failures)

    def printErrorList(self, flavour, errors):
        for test, err in errors:
            self.stream.writeln("%s: %s" % (
                flavour, self.getDescription(test)))
            self.stream.writeln("  %s" % "\n  ".join(err.split("\n")))


class FancyTestRunner(unittest.TextTestRunner):
    """A test runner class that displays results in textual form
    with fancy colors and unicode characters.
    """
    def __init__(self, stream=sys.stderr, descriptions=1, verbosity=1):
        self.stream = _StylizeWritelnDecorator(stream)
        self.descriptions = descriptions
        self.verbosity = verbosity

    def _makeResult(self):
        return _FancyTestResult(self.stream, self.descriptions, self.verbosity)

    def run(self, test):
        "Run the given test case or test suite."
        result = self._makeResult()
        startTime = time.time()
        test(result)
        stopTime = time.time()
        timeTaken = stopTime - startTime
        result.printErrors()
        run = result.testsRun
        if not result.wasSuccessful():
            self.stream.write("%s FAILED " % result.ballot_x, style='red')
            self.stream.write('(')
            failed, errored = map(len, (result.failures, result.errors))
            if failed:
                self.stream.write("failures=%d" % failed)
            if errored:
                if failed:
                    self.stream.write(", ")
                self.stream.write("errors=%d" % errored)
            self.stream.write(", tests=%d" % (run))
            self.stream.writeln(") (%.3fs)" % timeTaken)
        else:
            self.stream.writeln()
            self.stream.writeln("%s OK %d test%s complete" % (
                result.check_mark, run, run != 1 and "s" or ""),
                style='green:bold')
        return result
