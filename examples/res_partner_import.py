#! /usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright 2016 Antonio Espinosa (http://github.com/antespi)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging
from collections import OrderedDict
from odooetl import cli, importer, parsers, filters

_logger = logging.getLogger(__name__)


class PartnerImport(importer.BaseImport):
    main_model = 'res.partner'
    unassigned_fields = ['email']

    def item_mandatory_fields(self):
        return ['Name']

    def search_config_map(self):
        return OrderedDict([
            ('name', filters.FilterStringify(fields='Name')),
        ])

    def update_config_map(self):
        return OrderedDict([
            ('email', filters.FilterEmail(fields='Email')),
        ])


if __name__ == '__main__':
    cli.CliApplication().run(PartnerImport(parser=parsers.ParserCSV()))
