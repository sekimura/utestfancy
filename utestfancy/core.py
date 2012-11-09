# -*- coding: utf-8 -*-
import time
import sys
import unittest

try:
    # python 2.7
    from unittest.signals import registerResult
except ImportError:
    # python 2.6
    import weakref
    _results = weakref.WeakKeyDictionary()

    def registerResult(result):
        _results[result] = 1


class TestProgram(unittest.TestProgram):
    def __init__(self, *args, **kwargs):
        if not hasattr(kwargs, 'testRunner'):
            kwargs['testRunner'] = FancyTestRunner
        super(TestProgram, self).__init__(*args, **kwargs)

main = TestProgram


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
            stash[0].insert(0, '\033[%sm' % style_map[style][0])
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


class FancyTestResult(unittest.TestResult):
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
    separator1 = '=' * 70
    separator2 = '-' * 70

    def __init__(self, stream, descriptions, verbosity):
        super(FancyTestResult, self).__init__()
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
        super(FancyTestResult, self).startTest(test)
        if self.showAll:
            desc = self.getShortTestCaseClassDescription(test)
            if self._last_class_desc != desc:
                self.stream.writeln()
                self.stream.writeln('%s %s' % (
                    self.white_diamond_suit, desc), style='bold')
                self.stream.writeln()
                self._last_class_desc = desc

    def addSuccess(self, test):
        super(FancyTestResult, self).addSuccess(test)
        if self.showAll:
            self.stream.write('  %s' % self.check_mark, style='green:bold')
            self.stream.writeln(' %s' % self.getDescription(test))
        elif self.dots:
            self.stream.write('.', style='green')
            self.stream.flush()

    def addError(self, test, err):
        super(FancyTestResult, self).addError(test, err)
        if self.showAll:
            self.stream.write('  %s' % self.ballot_x, style='yellow:bold')
            self.stream.writeln(' %s' % self.getDescription(test),
                                style='yellow')
        elif self.dots:
            self.stream.write('E', style='yellow')
            self.stream.flush()

    def addFailure(self, test, err):
        super(FancyTestResult, self).addFailure(test, err)
        if self.showAll:
            self.stream.write('  %s' % self.ballot_x, style='red:bold')
            self.stream.writeln(' %s' % self.getDescription(test), style='red')
        elif self.dots:
            self.stream.write('F', style='red')
            self.stream.flush()

    def addSkip(self, test, reason):
        super(FancyTestResult, self).addSkip(test, reason)
        if self.showAll:
            self.stream.write("  - ", style='cyan:bold')
            self.stream.writeln("%s ... %s" % (
                                reason, self.getDescription(test)))
        elif self.dots:
            self.stream.write("s", style='cyan')
            self.stream.flush()

    def addExpectedFailure(self, test, err):
        super(FancyTestResult, self).addExpectedFailure(test, err)
        if self.showAll:
            self.stream.write("  * ", style='cyan:bold')
            self.stream.writeln("expected failure ... %s" % (
                                self.getDescription(test)))
        elif self.dots:
            self.stream.write("x", style='cyan')
            self.stream.flush()

    def addUnexpectedSuccess(self, test):
        super(FancyTestResult, self).addUnexpectedSuccess(test)
        if self.showAll:
            self.stream.write("  * ", style='cyan:bold')
            self.stream.writeln("unexpected success ... %s" % (
                                self.getDescription(test)))
        elif self.dots:
            self.stream.write("u", style='cyan')
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
            self.stream.writeln(self.separator1)
            self.stream.writeln("%s: %s" % (
                flavour, self.getDescription(test)))
            self.stream.writeln(self.separator2)
            self.stream.writeln("  %s" % "\n  ".join(err.split("\n")))


class FancyTestRunner(unittest.TextTestRunner):
    """A test runner class that displays results in textual form
    with fancy colors and unicode characters.
    """
    resultclass = FancyTestResult

    def __init__(self, *args, **kwargs):
        if hasattr(super(FancyTestRunner, self), 'failtest'):
            super(FancyTestRunner, self).__init__(*args, **kwargs)
        else:
            super(FancyTestRunner, self).__init__(
                stream=kwargs.get('stream', sys.stderr),
                descriptions=kwargs.get('descriptions', 1),
                verbosity=kwargs.get('verbosity', 1),
            )
        self.stream = _StylizeWritelnDecorator(self.stream.stream)

    def _makeResult(self):
        return self.resultclass(self.stream, self.descriptions, self.verbosity)

    def run(self, test):
        "Run the given test case or test suite."
        result = self._makeResult()
        registerResult(result)
        if hasattr(self, 'failfast'):
            result.failfast = self.failfast
        if hasattr(self, 'buffer'):
            result.buffer = self.buffer
        startTime = time.time()
        startTestRun = getattr(result, 'startTestRun', None)
        if startTestRun is not None:
            startTestRun()
        try:
            test(result)
        finally:
            stopTestRun = getattr(result, 'stopTestRun', None)
            if stopTestRun is not None:
                stopTestRun()
        stopTime = time.time()
        timeTaken = stopTime - startTime
        result.printErrors()
        if hasattr(result, 'separator2'):
            self.stream.writeln(result.separator2)
        else:
            self.stream.writeln()
        run = result.testsRun
        self.stream.writeln("Ran %d test%s in %.3fs" %
                            (run, run != 1 and "s" or "", timeTaken),
                            style='grey')
        self.stream.writeln()

        expectedFails = unexpectedSuccesses = skipped = 0
        try:
            results = map(len, (result.expectedFailures,
                                result.unexpectedSuccesses,
                                result.skipped))
        except AttributeError:
            pass
        else:
            expectedFails, unexpectedSuccesses, skipped = results

        infos = []
        if not result.wasSuccessful():
            self.stream.write("%s FAILED" % result.ballot_x, style='red:bold')
            failed, errored = map(len, (result.failures, result.errors))
            if failed:
                infos.append("failures=%d" % failed)
            if errored:
                infos.append("errors=%d" % errored)
        else:
            self.stream.write("%s OK" % result.check_mark, style='green:bold')
        if skipped:
            infos.append("skipped=%d" % skipped)
        if expectedFails:
            infos.append("expected failures=%d" % expectedFails)
        if unexpectedSuccesses:
            infos.append("unexpected successes=%d" % unexpectedSuccesses)
        if infos:
            self.stream.writeln(" (%s)" % (", ".join(infos),))
        else:
            self.stream.write("\n")
        return result
