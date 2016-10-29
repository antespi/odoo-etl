# -*- coding: utf-8 -*-
# Copyright 2016 Antonio Espinosa (http://github.com/antespi)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging
from collections import OrderedDict
from . import etl

_logger = logging.getLogger(__name__)


class BaseImport(etl.BaseETL):
    avoid_create = False

    def cleanup(self):
        pass

    def item_not_found(self, item, mapped):
        current = super(BaseImport, self).item_not_found(item, mapped)
        if not current and self.avoid_create:
            _logger.warning(
                "%3d [?] '%s' ... Not found and create disabled",
                self.n, self.item_show(current, item, mapped))
            return None
        return current

    def process(self):
        with self.parser_open() as parser:
            self.n = self.options.start if self.options.start > 0 else 1
            for item in parser:
                current = None
                sconfig = uconfig = aconfig = OrderedDict()
                smap = umap = amap = {}
                if self.item_check(item):
                    # Data for search/create
                    sconfig = self.search_config_map()
                    smap = self.item_mapping(None, item, config=sconfig)
                    smap = self.search_pre_mapping(item, smap)

                    # Search item
                    current = self.item_search(item, smap)
                    smap = self.search_post_mapping(current, item, smap)

                    # Do not create/update item (current is None)
                    # Item not found (current is False), create it
                    if current is False:
                        current = self.item_create(item, smap)
                    # Update item (current)
                    if current:
                        uconfig = self.update_config_map()
                        umap = self.item_mapping(current, item, config=uconfig)
                        umap = self.update_pre_mapping(current, item, umap)
                        if umap:
                            self.item_write(current, item, umap)
                        # Translate fields
                        self.item_translate(current, item, umap)
                        # Related data
                        self.item_related(current, item, umap)
                        # Log access magic fields
                        aconfig = self.access_config_map()
                        amap = self.item_mapping(current, item, config=aconfig)
                        amap = self.access_pre_mapping(current, item, amap)
                        if amap:
                            self.item_access(current, item, amap)

                # Log mapped data
                sconfig.update(uconfig)
                sconfig.update(aconfig)
                smap.update(umap)
                smap.update(amap)
                self.item_log(current, item, sconfig.keys(), smap)
                self.n += 1
