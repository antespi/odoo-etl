# -*- coding: utf-8 -*-
# Copyright 2016 Antonio Espinosa (http://github.com/antespi)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import os
from yaml.parser import ParserError
from unittest import TestCase
from odooetl.tools import (
    getmethod, dict_recursive_update, config_read, config_get, uniquify,
)


class TestSafeEval(TestCase):
    attribute = 1

    def method(self):
        pass

    def test_getmethod(self):
        self.assertEqual(self.method, getmethod(self, 'method'))
        self.assertEqual(None, getmethod(self, 'nomethod'))
        self.assertEqual(None, getmethod(self, 'attribute'))
        self.assertEqual({}, getmethod(self, 'attribute', {}))

    def test_dict_recursive_update(self):
        a = {
            'one': 1,
            'depth': {
                'two': 2,
                'three': 3,
            },
        }
        b = {
            'one': -1,
            'depth': {
                'two': -2,
                'four': -4
            },
            'five': -5,
        }
        result = {
            'one': -1,
            'depth': {
                'two': -2,
                'three': 3,
                'four': -4,
            },
            'five': -5,
        }
        a = dict_recursive_update(a, b)
        self.assertEqual(result, a)

    def test_config(self):
        result = {
            'odoo': {
                'protocol': 'xmlrpc',
                'host': 'localhost',
                'port': 8069,
                'scheme': 'http',
                'username': 'admin',
                'password': 'admin',
                'dbname': 'test',
            },
            'parsers': {
                'csv': {
                    'delimiter': ',',
                },
            },
        }
        root = os.path.dirname(os.path.abspath(__file__))
        validfile = os.path.join(root, 'data/config_test_valid.yaml')
        invalidfile = os.path.join(root, 'data/config_test_invalid.yaml')
        with self.assertRaises(IOError):
            config_read('not_found.yaml')
        with self.assertRaises(ParserError):
            config = config_read(invalidfile)
        config = config_read(validfile)
        self.assertEqual(result, config)
        self.assertEqual(8069, config_get(config, 'odoo.port'))
        self.assertEqual('http', config_get(config, 'odoo.scheme'))
        self.assertEqual(',', config_get(config, 'parsers.csv.delimiter'))
        self.assertEqual(None, config_get(config, 'not.found'))
        self.assertEqual(None, config_get(config, False))

    def test_uniquify(self):
        cases = (
            [1, 1, 2, 3, 4],
            [1, 2, 2, 3, 4],
            [1, 2, 3, 4, 4],
            [1, 1, 1, 2, 1, 3, 2, 4, 3, 4, 4],
        )
        result = [1, 2, 3, 4]
        for case in cases:
            self.assertEqual(result, uniquify(case))
