# -*- coding: utf-8 -*-
# Copyright 2016 Antonio Espinosa (http://github.com/antespi)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from .base import BaseFilter, float_normalize, integer_normalize
from ..safe_eval import expr_eval


class FilterNumber(BaseFilter):

    def __init__(self, fields=None, default=0, config={}):
        super(FilterNumber, self).__init__(
            fields=fields, default=default, config=config)
        self.type = self.config.get('type', 'integer')
        self.precision = self.config.get('precision', 2)
        self.operator = self.config.get('operator', '+')
        self.stringify = self.config.get('stringify', False)

    def apply(self, value):
        if self.type == 'integer':
            value = integer_normalize(value)
        else:
            value = float_normalize(value, self.precision)
        return str(value) if self.stringify else value

    def map(self, item, mapped={}):
        operators_available = ('+', '-', '*', '/', '%')
        if isinstance(self.fields, (str, unicode)):
            value = item[self.fields] if self.fields in item else self.default
        elif isinstance(self.fields, (list, tuple)):
            # Operator mode, same operator for all fields
            parts = [str(self.apply(item[s]))
                     for s in self.fields if s in item]
            operator = self.operator
            if operator not in operators_available:
                operator = '+'
            formula = ' %s ' % operator
            formula = formula.join(parts)
            value = expr_eval(formula)
            # TODO : Formula mode, custom formula with fields substitution
        else:
            value = self.default
        return self.apply(value)


class FilterInteger(FilterNumber):

    def __init__(self, fields=None, default=0, config={}):
        config = config or {}
        config['type'] = 'integer'
        super(FilterInteger, self).__init__(
            fields=fields, default=default, config=config)


class FilterFloat(FilterNumber):

    def __init__(self, fields=None, default=0., config={}):
        config = config or {}
        config['type'] = 'float'
        super(FilterFloat, self).__init__(
            fields=fields, default=default, config=config)
