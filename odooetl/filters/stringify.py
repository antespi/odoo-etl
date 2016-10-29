# -*- coding: utf-8 -*-
# Copyright 2016 Antonio Espinosa (http://github.com/antespi)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import re
from .base import BaseFilter, stringify


class FilterStringify(BaseFilter):

    def __init__(self, fields=None, default=False, config={}):
        super(FilterStringify, self).__init__(
            fields=fields, default=default, config=config)
        self.separator = self.config.get('separator', False)
        self.replace = self.config.get('replace', False)
        self.if_empty = self.config.get('if_empty', False)
        self.min_length = self.config.get('min', 0)
        self.lfillchar = self.config.get('lfill', '')
        self.rfillchar = self.config.get('rfill', '')
        self.allowed_chars = self.config.get('allowed_chars', '')

    def apply(self, value):
        value = stringify(value)
        if value and self.allowed_chars:
            pattern = r'' + '[^' + self.allowed_chars + ']'
            value = re.sub(pattern, '', value)
        if value and self.replace and isinstance(self.replace, (list, tuple)):
            for r in self.replace:
                if len(r) == 2:
                    value = value.replace(r[0], r[1])
        if value and len(value) < self.min_length:
            if self.lfillchar:
                value = value.rjust(self.min_length, self.lfillchar)
            if self.rfillchar:
                value = value.ljust(self.min_length, self.rfillchar)
        if not value and self.if_empty is not None:
            value = self.if_empty
        return value

    def map(self, item, mapped={}):
        if isinstance(self.fields, (str, unicode)):
            value = item[self.fields] if self.fields in item else self.default
        elif isinstance(self.fields, (list, tuple)):
            parts = []
            for s in self.fields:
                part = stringify(item[s]) if s in item else ''
                if part:
                    parts.append(part)
            if (len(parts) > 0):
                if self.separator is not False:
                    value = self.separator.join(parts)
                else:
                    if isinstance(self.fields, list):
                        value = ' '.join(parts)
                    else:
                        value = ''.join(parts)
            else:
                value = self.default
        else:
            value = self.default
        if value == self.default:
            return self.default
        return self.apply(value)
