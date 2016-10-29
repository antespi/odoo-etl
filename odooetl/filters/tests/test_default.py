# -*- coding: utf-8 -*-
# Copyright 2016 Antonio Espinosa (http://github.com/antespi)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from unittest import TestCase
from odooetl.filters import FilterDefault


class TestDefault(TestCase):

    def test_apply(self):
        f = FilterDefault(default='default')
        self.assertEqual('default', f.apply('value'))

    def test_map(self):
        item = {'f1': 'value'}
        f = FilterDefault(fields='f1', default='default')
        self.assertEqual('default', f.map(item))
        item = {}
        self.assertEqual('default', f.map(item))
