# -*- coding: utf-8 -*-
# Copyright 2016 Antonio Espinosa (http://github.com/antespi)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import os
from unittest import TestCase
from odooetl.parsers import ParserCSV


class TestCSV(TestCase):

    def _read(self, parser, filename):
        result = [
            {'f1': '1', 'f2': '1.1', 'f3': 'r1_c3', 'f4': 'año', },
            {'f1': '2', 'f2': '1.2', 'f3': 'r2_c3', 'f4': 'word', },
            {'f1': '3', 'f2': '1.3', 'f3': 'r3_c3', 'f4': 'wörd', },
        ]
        root = os.path.dirname(os.path.abspath(__file__))
        testfile = os.path.join(root, filename)
        mapped = []
        with parser.open(testfile):
            for item in parser:
                mapped.append(item)
        self.assertEqual(result, mapped)

    def test_read(self):
        self._read(ParserCSV(), 'data/csv_test_read.csv')

    def test_delimiter(self):
        parser = ParserCSV()
        parser.load(config={'delimiter': ';'})
        self._read(parser, 'data/csv_test_delimiter.csv')

    def test_mapping(self):
        parser = ParserCSV(mapping={'x1': 'f1', 'x2': 'f2', 'x9': 'f9'})
        self._read(parser, 'data/csv_test_mapping.csv')

    def test_limit(self):
        parser = ParserCSV()
        parser.load(start=2, limit=3)
        self._read(parser, 'data/csv_test_limit.csv')

    def test_notfund(self):
        parser = ParserCSV()
        with self.assertRaises(IOError):
            self._read(parser, 'data/csv_test_not_found.csv')

    def test_cannot_iterate(self):
        parser = ParserCSV()
        with self.assertRaises(RuntimeError):
            for item in parser:
                pass
        with self.assertRaises(RuntimeError):
            parser.next()
        parser.close()

    # TODO: Test write
