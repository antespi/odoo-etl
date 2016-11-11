# -*- coding: utf-8 -*-
# Copyright 2016 Antonio Espinosa (http://github.com/antespi)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from unittest import TestCase
from odooetl.etl import BaseETL
from odooetl.filters import FilterStringify, FilterEmail

db = {}


class OdooFakeModel(object):

    def __init__(self, vals={}):
        self.write(vals)

    def search(self, domain):
        key = str(domain)
        if key in db:
            return db[key]
        return False

    def add(self, domain, value=None):
        global db
        key = str(domain)
        if not value:
            db[key] = [self]
        else:
            db[key] = value if type(value) is list else [value]

    def create(self, vals):
        global db
        obj = OdooFakeModel(vals)
        key = str([(k, '=', vals[k]) for k in sorted(vals.keys())])
        db[key] = [obj]
        return obj

    def write(self, vals):
        for k, v in vals.iteritems():
            setattr(self, k, v)
        return True

    def log_access_write(self, vals):
        return self.write(vals)

    def __str__(self):
        """String"""
        return str(self.__dict__)

    def __eq__(self, other):
        """Compare"""
        return self.__dict__ == other.__dict__ \
            if type(other) == OdooFakeModel else False

    def __ne__(self, other):
        """Compare"""
        return not self.__eq__(other)


class OdooFakeEnv(object):

    def __contains__(self, model_name):
        """Test whether the given model exists."""
        return True

    def __getitem__(self, model_name):
        """Return an empty recordset from the given model."""
        return OdooFakeModel()


class SampleETL(BaseETL):
    env = OdooFakeEnv()

    def item_mandatory_fields(self):
        res = super(SampleETL, self).item_mandatory_fields()
        res.append('name')
        return res


class TestETL(TestCase):

    def tearDown(self, *args, **kwargs):
        global db
        db = {}
        return super(TestETL, self).tearDown(*args, **kwargs)

    def test_item_check(self):
        etl = SampleETL()
        self.assertTrue(etl.item_check({'name': 'Paquito'}))
        self.assertFalse(etl.item_check({'name': ''}))
        self.assertFalse(etl.item_check({'name2': 'Paquito'}))

    def test_item_show(self):
        etl = SampleETL()
        current_a = type('OdooFakeModel', (OdooFakeModel,), {
            'display_name': 'My complete name',
            'name': 'MyName',
            'id': 1,
        })
        current_b = type('OdooFakeModel', (OdooFakeModel,), {
            'name': 'MyName',
            'id': 2,
        })
        current_c = type('OdooFakeModel', (OdooFakeModel,), {
            'id': 3,
        })
        item_a = {
            'name': 'ItemName',
            'xmlid': '__export__.item_a',
            'id': 4,
        }
        item_b = {
            'xmlid': '__export__.item_b',
            'id': 5,
        }
        item_c = {
            'id': 6,
        }
        mapped_a = {
            'name': 'MappedName',
            'xmlid': '__export__.mapped_a',
            'id': 7,
        }
        mapped_b = {
            'xmlid': '__export__.mapped_b',
            'id': 8,
        }
        mapped_c = {
            'id': 9,
        }
        self.assertEqual('My complete name',
                         etl.item_show(current_a, item_a, mapped_a))
        self.assertEqual('MyName',
                         etl.item_show(current_b, item_a, mapped_a))
        self.assertEqual('MappedName',
                         etl.item_show(current_c, item_a, mapped_a))
        self.assertEqual('ItemName',
                         etl.item_show(current_c, item_a, mapped_b))
        self.assertEqual('XML ID = __export__.mapped_b',
                         etl.item_show(current_c, item_b, mapped_b))
        self.assertEqual('XML ID = __export__.item_b',
                         etl.item_show(current_c, item_b, mapped_c))
        self.assertEqual('ID = 9',
                         etl.item_show(current_c, item_c, mapped_c))
        self.assertEqual('ID = 6',
                         etl.item_show(current_c, item_c, {}))
        self.assertEqual('ID = 3',
                         etl.item_show(current_c, {}, {}))

    def test_item_query_get(self):
        etl = SampleETL()
        etl.main_model = 'res.partner'
        self.assertEqual([{
            'mode': 'direct',
            'domain': [('id', '=', 1)],
        }], etl.item_query_get({}, {'id': 1}))
        self.assertEqual([{
            'mode': 'xmlid',
            'domain': [
                ('module', '=', 'base'),
                ('name', '=', 'sample'),
                ('model', '=', 'res.partner'),
            ],
        }], etl.item_query_get({}, {'xmlid': 'base.sample'}))
        self.assertEqual([{
            'mode': 'direct',
            'domain': [('name', '=ilike', 'MyName')],
        }], etl.item_query_get({}, {'name': 'MyName'}))
        self.assertEqual([], etl.item_query_get({}, {'xmlid': 'sample'}))

    def test_item_search(self):
        global db
        domain_xmlid = [
            ('module', '=', 'base'),
            ('name', '=', 'sample'),
            ('model', '=', 'res.partner'),
        ]
        partner_xmlid = OdooFakeModel({
            'model': 'res.partner',
            'res_id': 1,
        })
        data = {
            'id': 1,
            'name': 'MyName',
        }
        partner = OdooFakeModel(data)
        result = OdooFakeModel(data)
        other = OdooFakeModel({
            'id': 2,
            'name': 'MyName2',
        })
        # Populate DB
        partner_xmlid.add(domain_xmlid)
        partner.add([('id', '=', 1)])
        partner.add([('name', '=', 'MyName')])
        partner.add([('name', '=ilike', 'MyName')])
        partner.add([('name', 'ilike', 'MyName')], value=[partner, other])
        etl = SampleETL()
        query = {
            'mode': 'xmlid',
            'domain': domain_xmlid,
        }
        self.assertFalse(etl.item_search_query(query, {}, {}))
        etl.main_model = 'res.partner'
        self.assertEqual(result, etl.item_search_query(query, {}, {}))
        query = {
            'mode': 'xmlid',
            'domain': [
                ('module', '=', 'base'),
                ('name', '=', 'other'),
                ('model', '=', 'res.partner'),
            ],
        }
        self.assertFalse(etl.item_search_query(query, {}, {}))
        query = {
            'mode': 'direct',
            'domain': [
                ('name', '=', 'MyName'),
            ],
        }
        self.assertEqual(result, etl.item_search_query(query, {}, {}))
        query = {
            'mode': 'direct',
            'domain': [
                ('name', 'ilike', 'MyName'),
            ],
        }
        self.assertEqual(result, etl.item_search_query(query, {}, {}))
        query = {
            'mode': 'direct',
            'domain': [
                ('name', '=', 'OtherName'),
            ],
        }
        self.assertFalse(etl.item_search_query(query, {}, {}))
        self.assertFalse(etl.item_search({}, {}))
        self.assertEqual(result, etl.item_search({}, {'name': 'MyName'}))

    def test_item_create(self):
        etl = SampleETL()
        etl.main_model = 'res.partner'
        data = {
            'name': 'MyName',
        }
        result = OdooFakeModel(data)
        self.assertEqual(result, etl.item_create({}, data))
        self.assertFalse(etl.item_create({}, {}))
        self.assertFalse(etl.item_create({}, {'_fake': 'Fake'}))
        self.assertFalse(etl.item_create({}, [1, 2]))

    def test_item_write(self):
        etl = SampleETL()
        etl.main_model = 'res.partner'
        data = {'name': 'MyName'}
        orig = OdooFakeModel({'id': 1})
        current = OdooFakeModel({'id': 1})
        result = OdooFakeModel({
            'id': 1,
            'name': 'MyName',
        })
        self.assertTrue(etl.item_write(current, {}, {}))
        self.assertEqual(orig, current)
        self.assertTrue(etl.item_write(current, {}, {'_fake': 'Fake'}))
        self.assertEqual(orig, current)
        self.assertTrue(etl.item_write(current, {}, [1, 2]))
        self.assertEqual(orig, current)
        self.assertTrue(etl.item_write(current, {}, data))
        self.assertEqual(result, current)

    def test_item_access(self):
        etl = SampleETL()
        etl.main_model = 'res.partner'
        data = {'create_date': '2016-11-06'}
        orig = OdooFakeModel({'id': 1, 'name': 'MyName'})
        current = OdooFakeModel({'id': 1, 'name': 'MyName'})
        result = OdooFakeModel({
            'id': 1,
            'name': 'MyName',
            'create_date': '2016-11-06',
        })
        self.assertTrue(etl.item_access(current, {}, {}))
        self.assertEqual(orig, current)
        self.assertTrue(etl.item_access(current, {}, {'name': 'OtherName'}))
        self.assertEqual(orig, current)
        self.assertTrue(etl.item_access(current, {}, [1, 2]))
        self.assertEqual(orig, current)
        self.assertTrue(etl.item_access(current, {}, data))
        self.assertEqual(result, current)

    def test_item_translate(self):
        etl = SampleETL()
        etl.main_model = 'res.partner'
        etl.translate_fields = ['name']
        etl.translate_langs = ['es_ES']
        current = OdooFakeModel({'id': 1, 'name': 'MyName'})
        domain = [
            ('lang', '=', 'es_ES'),
            ('name', '=', 'res.partner,name'),
            ('res_id', '=', 1),
            ('state', '=', 'translated'),
            ('type', '=', 'model'),
            ('value', '=', 'OtherName'),
        ]
        self.assertTrue(etl.item_translate(current, {}, {}))
        self.assertFalse(current.search(domain))
        self.assertTrue(etl.item_translate(
            current, {'name-es_ES': 'OtherName'}, {'name': ''}))
        self.assertFalse(current.search(domain))
        self.assertTrue(etl.item_translate(
            current, {'name-es_ES': None}, {'name': 'MyName'}))
        self.assertFalse(current.search(domain))
        self.assertTrue(etl.item_translate(
            current, {'name-es_ES': 'OtherName'}, {'name': 'MyName'}))
        translated = current.search(domain)[0]
        domain_update = [
            ('res_id', '=', 1),
            ('type', '=', 'model'),
            ('name', '=', 'res.partner,name'),
            ('lang', '=', 'es_ES'),
        ]
        translated.add(domain_update)
        self.assertEqual('OtherName', translated.value)
        self.assertTrue(etl.item_translate(
            current, {'name-es_ES': 'OtherName2'}, {'name': 'MyName'}))
        translated = current.search(domain_update)[0]
        self.assertEqual('OtherName2', translated.value)

    def test_item_mapping(self):
        item = {
            'Name': 'MyName ',
            'Email': 'myname@example.org\n',
        }
        result = {
            'name': 'MyName',
            'email': 'myname@example.org',
            'fix': 10,
        }
        etl = SampleETL()
        self.assertEqual({}, etl.item_mapping(None, item))
        self.assertEqual(result, etl.item_mapping(None, item, config={
            'name': FilterStringify(fields='Name'),
            'email': FilterEmail(fields='Email'),
            'fix': 10,
        }))
