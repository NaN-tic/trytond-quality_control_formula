#!/usr/bin/env python
# The COPYRIGHT file at the top level of this repository contains the full
# copyright notices and license terms.
import unittest
import doctest
import trytond.tests.test_tryton
from trytond.tests.test_tryton import test_view, test_depends
from trytond.tests.test_tryton import doctest_setup, doctest_teardown


class QualityControlTestCase(unittest.TestCase):
    'Test QualityControl module'

    def setUp(self):
        trytond.tests.test_tryton.install_module(
            'quality_control_formula')

    def test0005views(self):
        'Test views'
        test_view('quality_control_formula')

    def test0006depends(self):
        'Test depends'
        test_depends()


def suite():
    suite = trytond.tests.test_tryton.suite()
    from trytond.modules.quality_control.tests import test_quality_control
    for test in test_quality_control.suite():
        if test not in suite:
            suite.addTest(test)
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(
        QualityControlTestCase))
    suite.addTests(doctest.DocFileSuite('scenario_quality_test.rst',
            setUp=doctest_setup, tearDown=doctest_teardown, encoding='utf-8',
            optionflags=doctest.REPORT_ONLY_FIRST_FAILURE))
    return suite
