# -*- coding: utf-8 -*-
# Copyright 2016 Antonio Espinosa (http://github.com/antespi)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from .base import BaseFilter


class FilterDefault(BaseFilter):
    def apply(self, value):
        return self.default

    def map(self, item, mapped={}):
        return self.default
