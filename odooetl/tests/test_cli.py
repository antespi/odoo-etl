# -*- coding: utf-8 -*-
# Copyright 2016 Antonio Espinosa (http://github.com/antespi)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import os
import sys
from unittest import TestCase
from odooetl.cli import CliApplication
from odooetl.etl import BaseETL

etl_have_run = False


class ParserFake(object):
    name = 'fake'

    def load(self, start=0, limit=0, config={}):
        pass


class SampleETL(BaseETL):

    def run(self):
        global etl_have_run
        etl_have_run = True


class TestCli(TestCase):

    def tearDown(self, *args, **kwargs):
        global etl_have_run
        etl_have_run = False
        return super(TestCli, self).tearDown(*args, **kwargs)

    def test_run(self):
        config = {
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
        options = {
            'config': config,
            'dry_run': False,
            'max': 0,
            'start': 0,
            'verbose': None,
        }
        root = os.path.dirname(os.path.abspath(__file__))
        validfile = os.path.join(root, 'data/config_test_valid.yaml')
        sys.argv = ['fake_prog', '-c', validfile, 'filename']
        self.assertFalse(etl_have_run)
        cli = CliApplication()
        cli.run(SampleETL(ParserFake()))
        self.assertTrue(etl_have_run)
        self.assertEqual(options, vars(cli.options))
        self.assertEqual(['filename'], cli.args)
