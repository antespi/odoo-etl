# -*- coding: utf-8 -*-
# Copyright 2016 Antonio Espinosa (http://github.com/antespi)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from unittest import TestCase
from odooetl.filters import FilterNumber, FilterInteger, FilterFloat


class TestNumber(TestCase):
    def test_integer(self):
        cases = {
            1: ['1', 1, 1.0, True],
            0: ['0', 0, 0.0, False, None, '', 'Hello', '2.2'],
            -2: ['-2', -2, -2.0, -2.4, -2.9],
            2: ['2', 2, 2.0, 2.4, 2.9],
        }
        f = FilterInteger()
        for result, v in cases.iteritems():
            for value in v:
                self.assertEqual(result, f.apply(value))

    def test_float(self):
        cases = {
            1.: ['1', 1, 1.0, True],
            0.: ['0', 0, 0.0, False, None, '', 'Bye'],
            -2.: ['-2', -2, -2.0],
            -2.4: [-2.4, -2.4, -2.401, -2.399],
            3.14: ['3.14', 3.14, 3.1416, 3.14159],
        }
        f = FilterFloat()
        for result, v in cases.iteritems():
            for value in v:
                self.assertEqual(result, f.apply(value))

    def _operator(self, cases, type):
        for result, (item, fields, operator) in cases.iteritems():
            config = {'type': type}
            if operator:
                config['operator'] = operator
            f = FilterNumber(fields=fields, config=config)
            self.assertEqual(result, f.map(item))

    def test_operator_integer(self):
        cases = {
            10: ({'f1': 5, 'f2': '5'}, ['f1', 'f2'], '+'),
            2: ({'f1': 5, 'f2': '-3'}, ['f1', 'f2'], '+'),
            7: ({'f1': 4, 'f2': '3'}, ['f1', 'f2'], None),
            9: ({'f1': 4, 'f2': '5'}, ['f1', 'f2'], ':'),
            3: ({'f1': 6, 'f2': '3'}, ['f1', 'f2'], '-'),
            8: ({'f1': '4', 'f2': '-4'}, ['f1', 'f2'], '-'),
            15: ({'f1': '3', 'f2': 5}, ['f1', 'f2'], '*'),
            -8: ({'f1': '-2', 'f2': 4}, ['f1', 'f2'], '*'),
            4: ({'f1': '12', 'f2': 3}, ['f1', 'f2'], '/'),
            5: ({'f1': '16', 'f2': 3}, ['f1', 'f2'], '/'),
            1: ({'f1': '4', 'f2': 3}, ['f1', 'f2'], '%'),
        }
        self._operator(cases, 'integer')

    def test_operator_float(self):
        cases = {
            10.: ({'f1': 5, 'f2': '5'}, ['f1', 'f2'], '+'),
            2.5: ({'f1': 5.5, 'f2': '-3'}, ['f1', 'f2'], '+'),
            7.3: ({'f1': 4.1, 'f2': '3.2'}, ['f1', 'f2'], None),
            8.12: ({'f1': 4.9, 'f2': '3.22'}, ['f1', 'f2'], ':'),
            2.9: ({'f1': 6, 'f2': '3.1'}, ['f1', 'f2'], '-'),
            8.5: ({'f1': '4', 'f2': '-4.5'}, ['f1', 'f2'], '-'),
            16.: ({'f1': '3.2', 'f2': 5}, ['f1', 'f2'], '*'),
            -8.4: ({'f1': '-2.1', 'f2': 4}, ['f1', 'f2'], '*'),
            4.0: ({'f1': '12', 'f2': 3}, ['f1', 'f2'], '/'),
            5.33: ({'f1': '16', 'f2': 3}, ['f1', 'f2'], '/'),
            0.6: ({'f1': '4', 'f2': 3.4}, ['f1', 'f2'], '%'),
        }
        self._operator(cases, 'float')

    def test_map_integer(self):
        item = {
            'f1': 1,
            'f2': '2',
            'f3': -3,
            'f4': '-4',
            'f5': 0,
            'f6': False,
            'f7': '',
            'f8': None,
            'f9': '0',
        }
        result = {
            'f1': 1,
            'f2': 2,
            'f3': -3,
            'f4': -4,
            'f5': 0,
            'f6': 0,
            'f7': 0,
            'f8': 0,
            'f9': 0,
        }
        for key, value in item.iteritems():
            self.assertEqual(result[key], FilterInteger(fields=key).map(item))
        self.assertEqual(0, FilterInteger(fields=None).map(item))

    def test_map_float(self):
        item = {
            'f1': 1,
            'f2': '2.5',
            'f3': -3.0,
            'f4': '-4',
            'f5': 0,
            'f6': False,
            'f7': '',
            'f8': None,
            'f9': '0.',
        }
        result = {
            'f1': 1.,
            'f2': 2.5,
            'f3': -3.,
            'f4': -4.,
            'f5': 0.,
            'f6': 0.,
            'f7': 0.,
            'f8': 0.,
            'f9': 0.,
        }
        for key, value in item.iteritems():
            self.assertEqual(result[key], FilterFloat(fields=key).map(item))
        self.assertEqual(0., FilterFloat(fields=None).map(item))
