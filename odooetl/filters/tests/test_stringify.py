# -*- coding: utf-8 -*-
# Copyright 2016 Antonio Espinosa (http://github.com/antespi)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from unittest import TestCase
from odooetl.filters import FilterStringify


class TestStringify(TestCase):

    def test_integer(self):
        self.assertEqual('5', FilterStringify().apply(5))
        self.assertEqual(False, FilterStringify().apply(0))

    def test_float(self):
        self.assertEqual('5', FilterStringify().apply(5.))
        self.assertEqual('5.1', FilterStringify().apply(5.1))
        self.assertEqual(False, FilterStringify().apply(0.))

    def test_unicode(self):
        self.assertEqual('Año', FilterStringify().apply(u'Año'))
        self.assertEqual(False, FilterStringify().apply(u''))

    def test_empty(self):
        self.assertEqual(False, FilterStringify().apply(False))
        self.assertEqual(False, FilterStringify().apply([]))
        self.assertEqual(False, FilterStringify().apply(None))
        f = FilterStringify(config={'if_empty': 'empty'})
        self.assertEqual('empty', f.apply(False))
        self.assertEqual('empty', f.apply([]))
        self.assertEqual('empty', f.apply(None))

    def test_cast(self):
        f = FilterStringify(config={'cast': True}, default=None)
        self.assertEqual(True, f.apply('True'))
        self.assertEqual(False, f.apply('FALSE'))
        self.assertEqual('f', f.apply('f'))
        self.assertEqual(4, f.apply('4'))
        self.assertEqual(-10, f.apply('-10'))
        self.assertEqual(2.5, f.apply('2.5'))
        self.assertEqual('+-1', f.apply('+-1'))
        self.assertEqual('+-1.5', f.apply('+-1.5'))
        self.assertEqual(False, f.apply({}))
        self.assertEqual('[1, 2]', f.apply([1, 2]))
        self.assertEqual(False, f.apply(None))

    def test_trailing_spaces(self):
        cases = {
            'word': ['word ', ' word', ' word '],
            'two words': ['two words ', ' two words', ' two words '],
            False: [' ', '   '],
        }
        f = FilterStringify()
        for result, v in cases.iteritems():
            for value in v:
                self.assertEqual(result, f.apply(value))

    def test_separator(self):
        item = {'f1': 'one', 'f2': 'two'}
        cases = {
            'one,two': (',', ['f1', 'f2']),
            'one, two': (', ', ['f1', 'f2']),
            'one:two': (':', ['f1', 'f2']),
            'one two': (' ', ['f1', 'f2']),
            'one two': (False, ['f1', 'f2']),
            'onetwo': (False, ('f1', 'f2')),
        }
        for result, (separator, fields) in cases.iteritems():
            f = FilterStringify(fields=fields, config={'separator': separator})
            self.assertEqual(result, f.map(item))

    def test_replace(self):
        f = FilterStringify(config={'replace': [('NAME', 'Dolly')]})
        self.assertEqual('Hello Dolly', f.apply('Hello NAME'))
        f = FilterStringify(config={
            'replace': (('NAME', 'Dolly'), ('SALUDATION', 'Mr.'))})
        self.assertEqual('Hello Mr. Dolly', f.apply('Hello SALUDATION NAME'))
        # Only list or tuple allowed, not dict
        f = FilterStringify(config={
            'replace': {'ONE': '1', 'TWO': '2'}})
        self.assertEqual('ONE TWO', f.apply('ONE TWO'))
        # Only lists or tuples of 2 elements for each replacement
        f = FilterStringify(config={
            'replace': (['ONE'], ('TWO',))})
        self.assertEqual('ONE TWO', f.apply('ONE TWO'))

    def test_allowed_chars(self):
        cases = {
            '1234': ['1a2b3c4d ', ' 12 34 ', '_12-3+4/'],
        }
        f = FilterStringify(config={'allowed_chars': '1-9'})
        for result, v in cases.iteritems():
            for value in v:
                self.assertEqual(result, f.apply(value))

    def test_fill(self):
        f = FilterStringify(config={'lfill': '0', 'min': 8})
        self.assertEqual('00001234', f.apply(1234))
        f = FilterStringify(config={'rfill': '_', 'min': 6})
        self.assertEqual('NAME__', f.apply(' NAME '))
        f = FilterStringify(config={'rfill': ' ', 'min': 6})
        self.assertEqual('NAME  ', f.apply(' NAME'))

    def test_map(self):
        item = {
            'f1': True,
            'f2': False,
            'f3': u'Año',
            'f4': None,
            'f5': 0,
            'f6': 1,
        }
        result = {
            'f1': 'True',
            'f2': False,
            'f3': 'Año',
            'f4': False,
            'f5': False,
            'f6': '1',
        }
        for key, value in item.iteritems():
            self.assertEqual(result[key],
                             FilterStringify(fields=key).map(item))
        self.assertEqual('True',
                         FilterStringify(fields=('f1', 'f2')).map(item))
        self.assertEqual('1', FilterStringify(fields=('f4', 'f6')).map(item))
        self.assertEqual(False,
                         FilterStringify(fields=('f2', 'f4')).map(item))
        # Only list or tuple allowed, not dict
        self.assertEqual(False,
                         FilterStringify(fields={}).map(item))
