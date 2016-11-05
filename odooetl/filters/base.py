# -*- coding: utf-8 -*-
# Copyright 2016 Antonio Espinosa (http://github.com/antespi)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import decimal
import logging

_logger = logging.getLogger(__name__)


def stringify(value):
    if not value:
        value = ''
    if isinstance(value, unicode):
        value = value.strip()
        value = value.encode('utf-8')
    if isinstance(value, float):
        value = str(value).replace('.0', '')
    if not isinstance(value, str):
        value = str(value)
    # Strip also NO-BREAK SPACEs
    value = value.replace('\xc2\xa0', ' ')
    value = value.strip()
    return value


def nospaces(value):
    value = stringify(value)
    if value:
        value = value.replace(' ', '')
    return value


def list_encode(l, encoding='utf-8'):
    encoded = []
    for v in l:
        if isinstance(v, unicode):
            encoded.append(v.encode(encoding))
        elif isinstance(v, str):
            encoded.append(v)
        else:
            encoded.append(str(v))
    return encoded


def boolean_normalize(value):
    false_str = ('false', '0', 'no', 'n', 'f', 'falso')
    true_str = ('true', '1', 'yes', 'si', 'sí', 's', 't', 'y', 'verdadero')
    if isinstance(value, bool):
        return value
    if isinstance(value, (str, unicode)):
        value = value.strip().lower()
        if isinstance(value, unicode):
            value = value.encode('utf-8')
        if value in false_str:
            return False
        if value in true_str:
            return True
    if isinstance(value, (int, long)):
        if (value == 0):
            return False
        else:
            return True
    # By default, False
    return False


def float_normalize(value, precision=2):
    try:
        if isinstance(value, bool) and value:
            value = 1.
        elif isinstance(value, (str, unicode)):
            value = value.replace(',', '')
            clean = value.replace('.', '', 1)
            clean = clean.replace('-', '')
            clean = clean.replace('+', '')
            value = float(value) if clean.isdigit() else 0.
        elif isinstance(value, (int, long, decimal.Decimal)):
            value = float(value)
        elif not isinstance(value, float):
            value = 0.
    except:
        pass
    if value and precision >= 0:
        return round(value, precision)
    return value


def integer_normalize(value):
    try:
        if isinstance(value, bool) and value:
            value = 1
        elif isinstance(value, (str, unicode)):
            value = value.replace(',', '')
            clean = value.replace('.', '', 1)
            clean = clean.replace('-', '')
            clean = clean.replace('+', '')
            value = int(value) if clean.isdigit() else 0
        elif isinstance(value, float):
            value = int(value)
        elif not isinstance(value, (int, long)):
            value = 0
    except:
        pass
    return value


class BaseFilter(object):

    def __init__(self, fields=None, default=None, config={}):
        self.fields = fields
        self.config = config or {}
        self.default = default

    def apply(self, value):
        return value

    def map(self, item, mapped={}):
        if isinstance(self.fields, (str, unicode)):
            return item.get(self.fields, self.default)
        return self.default

    def garbage_add(self, field, mapped, garbage):
        if isinstance(garbage, (str, unicode)):
            garbage = [garbage]
        if isinstance(garbage, list):
            current = mapped.get(field, False)
            if current:
                garbage = [current] + garbage
            mapped[field] = ' - '.join(list_encode(garbage))
        return mapped
