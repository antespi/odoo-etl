# -*- coding: utf-8 -*-
# Copyright 2016 Antonio Espinosa (http://github.com/antespi)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from unittest import TestCase
from odooetl.filters.base import stringify, nospaces, list_encode, BaseFilter


class TestBase(TestCase):

    def test_stringify(self):
        cases = {
            'word': (u'word', ' word', ' word ', 'word\n', 'word\t', 'word\r',
                     '\r\nword'),
            'año': (u'año', '  año  '),
            '1': (1.0, 1.00),
            '1.5': (1.5, 1.50),
        }
        for result, values in cases.iteritems():
            for value in values:
                self.assertEqual(result, stringify(value))

    def test_nospaces(self):
        cases = {
            'word': [' word', ' word  ', 'word '],
            'twowords': [' two words', ' two   words  ', 'two  words  '],
        }
        for result, values in cases.iteritems():
            for value in values:
                self.assertEqual(result, nospaces(value))

    def test_list_encode(self):
        self.assertEqual(
            ['one', 'two', 'año', 'None', '1', 'True'],
            list_encode([u'one', 'two', u'año', None, 1, True])
        )

    def test_garbage_add(self):
        mapped = {}
        mapped = BaseFilter().garbage_add('_garbage', mapped, 'one')
        self.assertEqual('one', mapped.get('_garbage'))
        mapped = BaseFilter().garbage_add('_garbage', mapped, ['two', 'three'])
        self.assertEqual('one - two - three', mapped.get('_garbage'))
        mapped = BaseFilter().garbage_add('_garbage', mapped, 25)
        self.assertEqual('one - two - three', mapped.get('_garbage'))
        mapped = BaseFilter().garbage_add('_garbage', mapped, True)
        self.assertEqual('one - two - three', mapped.get('_garbage'))
