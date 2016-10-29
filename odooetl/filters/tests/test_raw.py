# -*- coding: utf-8 -*-
# Copyright 2016 Antonio Espinosa (http://github.com/antespi)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from unittest import TestCase
from odooetl.filters import FilterRaw


class TestRaw(TestCase):

    def test_apply(self):
        cases = [
            'año', u'año',
            1, 0, 9,
            1., 0., 9.5,
            None,
            [], (), {},
            True, False,
        ],
        f = FilterRaw()
        for value in cases:
            self.assertEqual(value, f.apply(value))

    def test_map(self):
        item = {
            'string': 'año',
            'unicode': u'año',
            'integer_1': 1,
            'integer_0': 0,
            'integer_9': 9,
            'float_1': 1.,
            'float_0': 0.,
            'float_9.5': 9.5,
            'None': None,
            'list': [1, 2],
            'tuple': (1, (2, 3)),
            'dict': {'one': 1},
            'True': True,
            'False': False,
        }
        for key, value in item.iteritems():
            self.assertEqual(value, FilterRaw(fields=key).map(item))
        self.assertEqual(
            'default', FilterRaw(fields='nokey', default='default').map(item))
        self.assertEqual(
            'other', FilterRaw(fields=None, default='other').map(item))
