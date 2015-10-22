#!/usr/bin/env python
# -*- coding: utf-8 -*-


import sys
import unittest

def div(a, b):
    if isinstance(a, int):
        a = float(a)
    if isinstance(b, int):
        b = float(b)
    return a / b

class MyTest(unittest.TestCase):

    def test_div(self):
        actual = div(4, 2)
        expected = 2
        self.assertEqual(actual, expected)

        actual = div(1, 2)
        expected = 0.5
        self.assertEqual(actual, expected)



unittest.main(argv=sys.argv)
