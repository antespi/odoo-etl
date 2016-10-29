# -*- coding: utf-8 -*-
# Copyright 2016 Antonio Espinosa (http://github.com/antespi)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import os
import logging
from csv import DictReader

from . import base

_logger = logging.getLogger(__name__)


class ParserCSV(base.BaseParser):
    """Read/write CSV files

    File must be encoded in UTF-8
    Default delimiter is ','
    """

    name = 'csv'
    iterator = None

    def config_default(self):
        return {
            'delimiter': ',',
        }

    def open(self, source):
        res = super(ParserCSV, self).open(source)
        if os.path.exists(source):
            self.resource = open(source, 'rb')
        else:
            raise IOError("File '%s' not found" % source)
        return res

    def __iter__(self):
        """Iterator"""
        if self.resource:
            self.iterator = DictReader(
                self.resource, delimiter=self.config.get('delimiter', ','))
            while self.start > self.n:
                self.n += 1
                self.iterator.next()
            return self
        else:
            raise RuntimeError("CSV file not opened")

    def next(self):
        if self.iterator:
            if not self.limit or self.limit >= self.n:
                self.n += 1
                return self.map(self.iterator.next())
            else:
                raise StopIteration()
        raise RuntimeError("CSV iterator not created")

    def write(self, item):
        # TODO: Write this item to CSV file
        pass

    def close(self):
        self.iterator = None
        if self.resource:
            self.resource.close()
        return super(ParserCSV, self).close()
