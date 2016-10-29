# -*- coding: utf-8 -*-
# Copyright 2016 Antonio Espinosa (http://github.com/antespi)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from .base import BaseFilter, boolean_normalize
from ..safe_eval import bool_eval


class FilterBoolean(BaseFilter):

    def __init__(self, fields=None, default=False, config={}):
        super(FilterBoolean, self).__init__(
            fields=fields, default=default, config=config)
        self.values = self.config.get('values', False)
        self.operator = self.config.get('operator', 'and')

    def apply(self, value):
        value = boolean_normalize(value)
        if isinstance(self.values, (list, tuple)) and len(self.values) > 1:
            if value:
                return self.values[0]
            else:
                return self.values[1]
        return value

    def map(self, item, mapped={}):
        operators_available = ('and', 'or')
        if isinstance(self.fields, (str, unicode)):
            value = item[self.fields] if self.fields in item else self.default
        elif isinstance(self.fields, (list, tuple)):
            # Operator mode, same operator for all fields
            parts = [str(boolean_normalize(item[s]))
                     for s in self.fields if s in item]
            operator = self.operator
            if operator not in operators_available:
                operator = 'and'
            formula = ' %s ' % operator
            formula = formula.join(parts)
            value = bool_eval(formula)
            # TODO : Formula mode, custom formula with fields substitution
        else:
            value = self.default
        return self.apply(value)
