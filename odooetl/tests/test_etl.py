# -*- coding: utf-8 -*-
# Copyright 2016 Antonio Espinosa (http://github.com/antespi)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from unittest import TestCase
from odooetl.etl import BaseETL


class OdooFakeModel(object):

    def write(self, vals):
        return True

    def log_access_write(self, vals):
        return True


class OdooFakeEnv(object):

    def __contains__(self, model_name):
        """Test whether the given model exists."""
        return True

    def __getitem__(self, model_name):
        """Return an empty recordset from the given model."""
        return OdooFakeModel()


class SampleETL(BaseETL):
    def item_mandatory_fields(self):
        res = super(SampleETL, self).item_mandatory_fields()
        res.append('name')
        return res


class TestETL(TestCase):
    def test_item_check(self):
        etl = SampleETL()
        self.assertTrue(etl.item_check({'name': 'Paquito'}))
        self.assertFalse(etl.item_check({'name': ''}))
        self.assertFalse(etl.item_check({'name2': 'Paquito'}))
