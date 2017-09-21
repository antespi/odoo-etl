# -*- coding: utf-8 -*-
# Copyright 2017 Antonio Espinosa (http://github.com/antespi)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging
import re
import phonenumbers
from .base import BaseFilter
from .stringify import FilterStringify

_logger = logging.getLogger(__name__)


class FilterPhone(BaseFilter):

    def __init__(self, fields=None, default=False, config={}):
        super(FilterPhone, self).__init__(
            fields=fields, default=default, config=config)
        self.garbage = self.config.get('garbage', '_garbage')
        self.label = self.config.get('label', 'Phone')
        self.cc_field = self.config.get('country_code_field', '_country_code')
        self.cc_default = self.config.get('country_code_default', None)
        fmt_str = self.config.get('format', 'INTERNATIONAL')
        self.format = phonenumbers.PhoneNumberFormat.INTERNATIONAL
        fmt = getattr(phonenumbers.PhoneNumberFormat, fmt_str, None)
        if fmt:
            self.format = fmt
        self.separator = self.config.get('separator', False)
        self.replace = self.config.get('replace', False)
        self.allowed_chars = self.config.get('allowed_chars', '\+0-9')

    def cc_normalize(self, cc):
        cc = cc and str(cc) or None
        if cc:
            cc = cc.upper()[:2]
            # UK is an alias for GB
            if cc == 'UK':
                cc = 'GB'
        return cc

    def phone_check(self, phone, format, cc=None, allowed_chars='\+0-9'):
        pattern = r'' + '[^' + allowed_chars + ']'
        phone = phone or ''
        candidate = re.sub(pattern, '', phone)
        res = False
        if not candidate:
            return res
        prefix = ''
        if candidate.startswith('+'):
            prefix = '+'
        candidate = prefix + re.sub(r'\+', '', candidate)
        # Parse number
        number = False
        try:
            number = phonenumbers.parse(candidate, cc)
        # except Exception, e:
        except Exception:
            # Parse error
            # _logger.error("Bad phone number(%s) : %s" %
            #               (candidate, str(e)), 1)
            pass
        if number:
            if not phonenumbers.is_possible_number(number):
                # This phone has an invalid length for its country
                # _logger.error("Phone with invalid length(%s)" %
                #               candidate, 1)
                pass
            elif not phonenumbers.is_valid_number(number):
                # This phone has no dial in its country
                # _logger.error("Number is not a valid phone(%s)" %
                #               candidate, 1)
                pass
            else:
                res = phonenumbers.format_number(number, format)
        return res

    def apply(self, value):
        cc = self.cc_normalize(self.cc_default)
        value_ok = self.phone_check(
            value, self.format, cc=cc, allowed_chars=self.allowed_chars)
        if value_ok:
            return value_ok
        return self.default

    def map(self, item, mapped={}):
        replace = self.replace or []
        cc = self.cc_normalize(
            mapped.get(self.cc_field, None) or self.cc_default)
        f = FilterStringify(fields=self.fields, default=None, config={
            'replace': replace + [(' ', '')],
            'separator': self.separator
        })
        value = f.map(item)
        if value is None:
            return self.default
        phones = []
        if self.separator:
            values = value.split(self.separator)
        else:
            values = [value]
        for value in values:
            value_ok = self.phone_check(
                value, self.format, cc=cc, allowed_chars=self.allowed_chars)
            if value_ok:
                phones.append(value_ok)
            elif self.garbage:
                self.garbage_add(
                    self.garbage, mapped,
                    'Bad %s: %s' % (self.label.lower(), value))
        if not phones:
            return self.default
        if len(phones) > 1 and self.garbage:
            garbage = ['%s: %s' % (self.label, e) for e in phones[1:]]
            self.garbage_add(self.garbage, mapped, garbage)
        return phones[0]
