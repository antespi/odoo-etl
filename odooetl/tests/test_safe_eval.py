# -*- coding: utf-8 -*-
# Copyright 2016 Antonio Espinosa (http://github.com/antespi)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from unittest import TestCase
from odooetl.safe_eval import const_eval, bool_eval, expr_eval, safe_eval


class TestSafeEval(TestCase):

    def test_const_eval(self):
        self.assertEqual(const_eval('10'), 10)
        self.assertEqual(const_eval('1 + 2'), 3)
        self.assertEqual(
            const_eval("[1,2, (3,4), {'foo':'bar'}]"),
            [1, 2, (3, 4), {'foo': 'bar'}])
        with self.assertRaises(ValueError):
            const_eval('a + b')

    def test_bool_eval(self):
        self.assertFalse(bool_eval('True and False'))
        self.assertTrue(bool_eval('True or False'))
        with self.assertRaises(ValueError):
            bool_eval('True or a + b')

    def test_expr_eval(self):
        self.assertEqual(expr_eval('1 + 2'), 3)
        self.assertEqual(expr_eval('[1,2]*2'), [1, 2, 1, 2])
        with self.assertRaises(NameError):
            expr_eval("__import__('sys').modules")
        with self.assertRaises(ValueError):
            expr_eval("str(5)")

    def test_safe_eval(self):
        self.assertEqual(safe_eval('a + b', locals_dict={'a': 3, 'b': 4}), 7)
        self.assertEqual(safe_eval('str(5)'), "5")
        with self.assertRaises(NameError):
            safe_eval("__import__('sys').modules")
        with self.assertRaises(SyntaxError):
            safe_eval("a = 3; b = 4; a + b")
        with self.assertRaises(ValueError):
            safe_eval("open('filename')")
