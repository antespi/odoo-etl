# -*- coding: utf-8 -*-
# Copyright 2016 Antonio Espinosa (http://github.com/antespi)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from unittest import TestCase
from odooetl.filters import FilterBoolean


class TestBoolean(TestCase):
    def test_symbols(self):
        cases = {
            True: ['true', '1', 'yes', 'si', u'sí', 'sí', 's', 't', 'y', 1, 9,
                   'verdadero', 'True', 'Yes', 'sI', 'S', 'Y', 'VERDADERO',
                   True],
            False: ['false', '0', 'no', 'n', 'f', 'falso', 'False', 'No', 'N',
                    'F', 'FALSO', 0, False, None, [], (), {}, 'a'],
        }
        f = FilterBoolean()
        for result, v in cases.iteritems():
            for value in v:
                self.assertEqual(result, f.apply(value))

    def test_values(self):
        cases = {
            'is true': ['true', True, 'Y'],
            'is false': ['false', False, 'N'],
        }
        f = FilterBoolean(config={'values': ('is true', 'is false')})
        for result, v in cases.iteritems():
            for value in v:
                self.assertEqual(result, f.apply(value))

    def _operator(self, cases, operator=None):
        config = {}
        if operator:
            config['operator'] = operator
        for result, (item, fields) in cases.iteritems():
            f = FilterBoolean(fields=fields, config=config)
            self.assertEqual(result, f.map(item))

    def test_operator_and(self):
        cases = {
            True: ({'f1': 'yes', 'f2': 'si'}, ['f1', 'f2']),
            False: ({'f1': 'yes', 'f2': 'no'}, ('f1', 'f2')),
        }
        self._operator(cases, 'and')
        self._operator(cases, 'other')
        self._operator(cases)

    def test_operator_or(self):
        cases = {
            True: ({'f1': 'yes', 'f2': 'no'}, ['f1', 'f2']),
            False: ({'f1': 'N', 'f2': 'no'}, ('f1', 'f2')),
        }
        self._operator(cases, 'or')

    def test_map(self):
        item = {
            'f1': True,
            'f2': False,
            'f3': 'F',
            'f4': None,
            'f5': 0,
            'f6': 1,
        }
        result = {
            'f1': True,
            'f2': False,
            'f3': False,
            'f4': False,
            'f5': False,
            'f6': True,
        }
        for key, value in item.iteritems():
            self.assertEqual(result[key], FilterBoolean(fields=key).map(item))
        self.assertEqual(False, FilterBoolean(fields=None).map(item))
