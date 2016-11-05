# -*- coding: utf-8 -*-
# Copyright 2016 Antonio Espinosa (http://github.com/antespi)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging
from pprint import pformat
from collections import OrderedDict
try:
    import odoo
except:
    try:
        import openerp as odoo
    except:
        odoo = None
from . import tools, filters

_logger = logging.getLogger(__name__)


class BaseETL(object):
    options = {}
    args = {}
    config = {}
    env = None
    main_model = None
    unassigned_fields = []
    translate_fields = []
    translate_langs = []
    n = 0

    def __init__(self, parser=None):
        self.parser = parser

    def config_default(self):
        """Return default configuration dictionary"""
        return {
            'odoo': {
                'conf': '/etc/odoo/odoo-server.conf',
                'login': 'admin',
                'dbname': 'default',
                'context': {
                    'tracking_disable': True
                },
            },
        }

    def options_add(self, argp):
        """Add options to ArgumentParser object"""
        argp.add_argument(
            '-m', '--max', type=int, default=0, metavar='MAX',
            help="Max number of items to process"),
        argp.add_argument(
            '-s', '--start', type=int, default=0, metavar='START',
            help="Start from this item"),
        return argp

    def odoo_config_load(self):
        if odoo:
            odoo_conf = tools.config_get(self.config, 'odoo.conf')
            odoo.tools.config.parse_config(['--config=%s' % odoo_conf])
        else:
            _logger.critical("No odoo module loaded")

    def parser_open(self):
        if not self.parser:
            raise Exception('Parser not initialized')
        if len(self.args) >= 1:
            source = self.args[0]
            return self.parser.open(source)
        raise Exception('No input file defined')

    def parser_close(self):
        if not self.parser:
            raise Exception('Parser not initialized')
        return self.parser.close()

    def process(self):
        """Perform ETL operations inside Odoo environment: self.env"""
        raise NotImplementedError("No ETL process implemented")

    def load(self):
        self.config = self.config_default()
        if 'config' in self.options and self.options.config:
            tools.dict_recursive_update(self.config, self.options.config)
        if self.parser:
            config = tools.config_get(
                self.config, 'parsers.%s' % self.parser.name, {})
            self.parser.load(
                start=self.options.start, limit=self.options.max,
                config=config)

    def context_get(self, ctx={}):
        ctx = ctx or {}
        ctx.update(self.config.get('odoo', {}).get('context', {}))
        ctx.update(self.config.get('odoo', {}).get('context_add', {}))
        return ctx

    def odoo_env_get(self, cr, uid):
        if odoo:
            env = odoo.api.Environment(cr, uid, {})
            ctx = env['res.users'].context_get()
            return odoo.api.Environment(cr, uid, self.context_get(ctx))
        else:
            _logger.critical("No odoo module loaded")
        return None

    def xmlrpc_env_get(self, host, port, scheme, dbname, username, password):
        # TODO: Create a XML-RPC environment
        # TODO: Set dry-run to avoid create/write/delete ops
        return None

    def search_config_map(self):
        """Inherit to configure search mapping"""
        return OrderedDict()

    def update_config_map(self):
        """Inherit to configure update mapping"""
        return OrderedDict()

    def access_config_map(self):
        """Inherit to configure access fields mapping"""
        return OrderedDict()

    def item_mandatory_fields(self):
        """Inherit to configure mandatory fields in read item"""
        return []

    def item_check_mandatory(self, item, mandatory):
        for field in mandatory:
            if not filters.FilterStringify(field).map(item):
                return False
        return True

    def item_check(self, item):
        """Inherit to validate read item"""
        if not self.item_check_mandatory(item, self.item_mandatory_fields()):
            _logger.warning("%3d [?]: Bad format item" % self.n)
            _logger.debug('Bad Item = ' + pformat(item))
            return False
        return True

    def item_show(self, current, item, mapped):
        """Inherit to show found item in different way"""
        try:
            return current.display_name
        except:
            pass
        try:
            return current.name
        except:
            pass
        name = mapped.get('name', False) or item.get('name', False)
        if name:
            return name
        xmlid = mapped.get('xmlid', False) or item.get('xmlid', False)
        if xmlid:
            'XML ID = %s' % xmlid
        obj_id = mapped.get('id', False) or item.get('id', False)
        if obj_id:
            'ID = %s' % obj_id
        return 'ID = %s' % current.id if current else ''

    def item_query_get(self, item, mapped):
        """Inherit to define another searching criteria"""
        obj_id = mapped.get('id', False)
        obj_xmlid = mapped.get('xmlid', False)
        name = mapped.get('name', False)
        # Search by ID
        if obj_id:
            return [{
                'mode': 'direct',
                'domain': [('id', '=', obj_id)],
            }]
        # Search by XML ID
        if obj_xmlid:
            parts = obj_xmlid.split('.')
            if len(parts) > 1:
                module = parts[0]
                name = '.'.join(parts[1:])
                return [{
                    'mode': 'xmlid',
                    'domain': [
                        ('module', '=', module),
                        ('name', '=', name),
                        ('model', '=', self.main_model),
                    ],
                }]
        # Search by Name
        if name:
            return [{
                'mode': 'direct',
                'domain': [('name', '=ilike', name)],
            }]
        return []

    def item_not_found(self, item, mapped):
        """Called when item is not found"""
        _logger.info(
            "%3d [+] '%s' ... Not found",
            self.n, self.item_show(None, item, mapped))
        return False

    def item_search_query(self, query, item, mapped, model=None):
        current = False
        model = model or self.main_model
        _logger.debug(
            "( ) ItemSearch : '%s' query = %s", model, pformat(query))
        if not model:
            return False
        mode = query.get('mode', 'direct')
        domain = query.get('domain', [])
        ids = False
        if mode == 'direct':
            ids = self.env[model].search(domain)
        if mode == 'xmlid':
            xml_ids = self.env['ir.model.data'].search(domain)
            if xml_ids and len(xml_ids) > 0:
                xml_obj = xml_ids[0]
                ids = self.env[model].search([('id', '=', xml_obj.res_id)])
        if ids and len(ids) > 0:
            _logger.debug("( ) ItemSearch : %d items", len(ids))
            current = ids[0]
            if len(ids) == 1:
                _logger.info(
                    "%3d [#] '%s' ... Found via %s",
                    self.n, self.item_show(current, item, mapped),
                    pformat(domain))
                _logger.debug("( ) ItemSearch : obj = %s", current)
            else:
                _logger.warning(
                    "%3d [#] '%s' ... More than one found via %s",
                    self.n, self.item_show(current, item, mapped),
                    pformat(domain))
                _logger.debug("( ) ItemSearch : objs = %s", ids)
        return current

    def item_search(self, item, mapped, model=None):
        """Search Odoo object based in item data"""
        queries = self.item_query_get(item, mapped)
        current = False
        for query in queries:
            current = self.item_search_query(query, item, mapped, model=model)
            if current:
                return current
        if not current:
            current = self.item_not_found(item, mapped)
        return current

    def _temp_fields_remove(self, mapped):
        vals = {}
        if mapped and isinstance(mapped, dict):
            vals = {k: v for k, v in mapped.iteritems()
                    if not k.startswith('_')}
        return vals

    def _unassigned_fields_remove(self, current, item, mapped, fields=None):
        # Some fields is better not set if no value ('', None or False)
        fields = fields or self.unassigned_fields
        for field in fields:
            if not mapped.get(field, False):
                mapped.pop(field, None)
        return mapped

    def item_create_prepare(self, model, item, mapped):
        """Inherit to customize create vals"""
        return self._temp_fields_remove(mapped)

    def item_create(self, item, mapped, model=None):
        """Create Odoo object based in item data"""
        current = False
        model = model or self.main_model
        if mapped:
            vals = self.item_create_prepare(model, item, mapped)
            if vals:
                _logger.debug(
                    "(*) ItemCreate : '%s' data = %s", model, pformat(vals))
                current = self.env[model].create(vals)
            else:
                _logger.error("%3d [?] Empty vals on item create", self.n)
        return current

    def item_write_prepare(self, model, item, mapped):
        """Inherit to customize write vals"""
        return self._temp_fields_remove(mapped)

    def item_write(self, current, item, mapped, model=None):
        """Write Odoo object based in item data"""
        model = model or self.main_model
        if current and mapped:
            vals = self.item_write_prepare(model, item, mapped)
            if vals:
                _logger.debug(
                    "(*) ItemWrite : '%s' data = %s", model, pformat(vals))
                return current.write(vals)
            else:
                _logger.error("%3d [?] Empty vals on item write", self.n)
        return True

    def item_access_prepare(self, model, item, mapped):
        """Inherit to customize access fields vals"""
        vals = {}
        fields = ('create_date', 'create_uid', 'write_date', 'write_uid')
        if mapped and isinstance(mapped, dict):
            vals = {k: v for k, v in mapped.iteritems() if k in fields}
        return vals

    def item_access(self, current, item, mapped, model=None):
        """Write Odoo object access fields based in item data"""
        model = model or self.main_model
        if current and mapped and getattr(current, 'log_access_write'):
            vals = self.item_access_prepare(model, item, mapped)
            if vals:
                _logger.debug(
                    "(*) ItemAccess : '%s' data = %s", model, pformat(vals))
                return current.log_access_write(vals)
            else:
                _logger.error("%3d [?] Empty vals on item access", self.n)
        return True

    def item_translate(self, current, item, mapped, model=None):
        """Write Odoo object translatable fields based in item data"""
        model = model or self.main_model
        if not (current and mapped and
                self.translate_fields and self.translate_langs):
            return True
        for field in self.translate_fields:
            source = mapped.get(field, None)
            name = model + ',' + field
            if not source:
                continue
            for lang in self.translate_lang:
                f = filters.FilterStringify(
                    fields=field + '-' + lang, default=None)
                value = f.map(item)
                if value is not None:
                    trans = self.env['ir.translation'].search([
                        ('res_id', '=', current.id),
                        ('type', '=', 'model'),
                        ('name', '=', name),
                        ('lang', '=', lang),
                    ])
                    data = {
                        'value': value,
                        'state': 'translated',
                    }
                    if trans:
                        _logger.info(
                            "   [#] Translation (%s - %s) : %s",
                            name, lang, value)
                        trans.write(trans.id, data)
                    else:
                        _logger.info(
                            "   [+] Translation (%s - %s) : %s",
                            name, lang, value)
                        data.update({
                            'res_id': current.id,
                            'type': 'model',
                            'name': name,
                            'lang': lang,
                        })
                        self.env['ir.translation'].create(data)
        return True

    def item_related(self, current, item, mapped):
        """Inherit to create/update Odoo related object"""
        return True

    def item_mapping(self, current, item, config=None):
        """Map item data using config"""
        mapped = {}
        if not config:
            return mapped
        for k, v in config.iteritems():
            if isinstance(v, filters.BaseFilter):
                mapped[k] = v.map(item, mapped)
            else:
                mapped[k] = v
        return mapped

    def item_log(self, current, item, fields, mapped):
        # TODO: Log mapped data to file
        return True

    def search_pre_mapping(self, item, mapped):
        """Inherit to modified mapped data. Called before search Odoo object
        """
        return mapped

    def search_post_mapping(self, current, item, mapped):
        """Inherit to modified mapped data. Called after search Odoo object
        """
        return self._unassigned_fields_remove(current, item, mapped)

    def update_pre_mapping(self, current, item, mapped):
        """Inherit to modified mapped data. Called before update Odoo object
        """
        return self._unassigned_fields_remove(current, item, mapped)

    def access_pre_mapping(self, current, item, mapped):
        """Inherit to modified mapped data.

        Called before update Odoo object access field
        """
        return self._unassigned_fields_remove(current, item, mapped)

    def run(self):
        self.odoo_config_load()
        protocol = self.config.get('odoo', {}).get('protocol', 'native')
        dbname = self.config.get('odoo', {}).get('dbname', 'default')
        if protocol == 'xmlrpc':
            host = self.config.get('odoo', {}).get('host', 'localhost')
            port = self.config.get('odoo', {}).get('port', '8069')
            scheme = self.config.get('odoo', {}).get('scheme', 'http')
            username = self.config.get('odoo', {}).get('username', 'admin')
            password = self.config.get('odoo', {}).get('password', 'admin')
            self.env = self.xmlrpc_env_get(
                host, port, scheme, dbname, username, password)
            self.process()
        if protocol == 'native' and odoo:
            login = self.config.get('odoo', {}).get('login', 'admin')
            with odoo.api.Environment.manage():
                registry = odoo.modules.registry.RegistryManager.get(dbname)
                with registry.cursor() as cr:
                    self.root = self.odoo_env_get(cr, odoo.SUPERUSER_ID)
                    user = self.root['res.users'].search([
                        ('login', '=', login),
                    ])
                    if not user:
                        raise Exception("User '%s' not found" % login)
                    self.env = self.odoo_env_get(cr, user.id)
                    self.process()
                    try:
                        if self.options.dry_run:
                            cr.rollback()
                        else:
                            cr.commit()
                    except Exception:
                        cr.rollback()
                        raise
