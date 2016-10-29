# -*- coding: utf-8 -*-
# Copyright 2016 Antonio Espinosa (http://github.com/antespi)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging
from . import etl

_logger = logging.getLogger(__name__)


class BaseIterator(etl.BaseETL):

    def cleanup(self):
        pass

    def process(self):
        # TODO: Search and iterate per each object
        pass
