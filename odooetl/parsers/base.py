# -*- coding: utf-8 -*-
# Copyright 2016 Antonio Espinosa (http://github.com/antespi)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

_logger = logging.getLogger(__name__)


class BaseParser(object):
    name = "base"
    start = 0
    limit = 0
    n = 1
    source = None
    resource = None

    def __init__(self, mapping={}):
        self.mapping = mapping
        self.config = self.config_default()

    def __iter__(self):
        """Iterator"""
        return self

    def map(self, item):
        if self.mapping:
            for k, v in self.mapping.iteritems():
                if k in item:
                    item[v] = item.pop(k)
        return item

    def config_default(self):
        return {}

    def load(self, start=0, limit=0, config={}):
        self.start = start
        self.limit = limit
        if start:
            self.limit += (start - 1)
        if config:
            self.config.update(config)

    def __enter__(self):
        """Magic method for use this object in a with statement"""
        return self

    def open(self, source):
        """Open resource to parser: filename, database, ..."""
        self.resource = None
        return self

    def next(self):
        return StopIteration()

    def write(self, item):
        pass

    def __exit__(self, type, value, traceback):
        """Magic method for use this object in a with statement"""
        self.close()

    def close(self):
        """Close parsed resource"""
        self.resource = None
