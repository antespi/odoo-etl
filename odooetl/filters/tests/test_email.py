# -*- coding: utf-8 -*-
# Copyright 2016 Antonio Espinosa (http://github.com/antespi)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from unittest import TestCase
from odooetl.filters import FilterEmail


class TestEmail(TestCase):

    def test_valid(self):
        cases = {
            'contact@example.org': ' contact@example.org ',
            'contact@example.org': 'contact@ example.org',
            'wildcard+email@example.org': 'wildcard+email@example.org',
            'name.lastname@example.org': 'name.lastname@example.org',
            'contact@example.es.org': 'contact@example.es.org',
            'contact@example.org': 'Name Lastname <contact@example.org>',
        }
        for result, value in cases.iteritems():
            self.assertEqual(result, FilterEmail().apply(value))

    def test_invalid(self):
        cases = ['contact+example.org', 'Contact', '', '  @example.org',
                 'contact@  ', 0, 1, 5, [], {}, (), False, None, ]
        for value in cases:
            self.assertFalse(FilterEmail().apply(value))

    def test_map(self):
        item = {
            'f1': 'contact@example.org',
            'f2': '@example.org',
            'f3': 'Name Lastname <other@example.org>'
        }
        result = {
            'f1': 'contact@example.org',
            'f2': False,
            'f3': 'other@example.org',
        }
        mapped = {}
        for field in item.keys():
            mapped = FilterEmail(
                fields=field, config={'garbage': False}).map(item)
        self.assertTrue(result, mapped)

    def test_multi(self):
        item_valid = {
            'f1': ' contact@example.org',
            'f2': 'other@example.org ',
        }
        item_invalid = {
            'f1': '@example.org',
            'f2': 'other@example.org',
        }
        item_mix = {
            'f1': '@example.org,contact@example.org',
            'f2': 'other@example.org',
        }
        f = FilterEmail(fields=['f1', 'f2'], config={'separator': ','})
        self.assertEqual(False, f.map({}))
        mapped = {}
        self.assertEqual('contact@example.org', f.map(item_valid, mapped))
        self.assertEqual('Email: other@example.org', mapped.get('_garbage'))
        mapped = {}
        self.assertEqual('other@example.org', f.map(item_invalid, mapped))
        self.assertEqual('Bad email: @example.org', mapped.get('_garbage'))
        mapped = {}
        self.assertEqual('contact@example.org', f.map(item_mix, mapped))
        self.assertEqual(
            'Bad email: @example.org - Email: other@example.org',
            mapped.get('_garbage'))
