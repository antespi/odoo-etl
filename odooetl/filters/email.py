# -*- coding: utf-8 -*-
# Copyright 2016 Antonio Espinosa (http://github.com/antespi)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import re
from validate_email import validate_email
from .base import BaseFilter, nospaces
from .stringify import FilterStringify

MAIL_REGEX = r'.*<(.+@.+)>'


class FilterEmail(BaseFilter):

    def __init__(self, fields=None, default=False, config={}):
        super(FilterEmail, self).__init__(
            fields=fields, default=default, config=config)
        self.garbage = self.config.get('garbage', '_garbage')
        self.separator = self.config.get('separator', False)
        self.replace = self.config.get('replace', False)

    def regex(self, value):
        if value and re.match(MAIL_REGEX, value):
            value = re.sub(MAIL_REGEX, r'\1', value)
        return value

    def apply(self, value):
        value = self.regex(nospaces(value))
        if validate_email(value):
            return value
        return self.default

    def map(self, item, mapped={}):
        replace = self.replace or []
        f = FilterStringify(fields=self.fields, default=None, config={
            'replace': replace + [(' ', '')],
            'separator': self.separator
        })
        value = f.map(item)
        if value is None:
            return self.default
        emails = []
        if self.separator:
            values = value.split(self.separator)
        else:
            values = [value]
        for value in values:
            value = self.regex(nospaces(value))
            if validate_email(value):
                emails.append(value)
            elif self.garbage:
                self.garbage_add(self.garbage, mapped, 'Bad email: %s' % value)
        if not emails:
            return self.default
        if len(emails) > 1 and self.garbage:
            garbage = ['Email: %s' % e for e in emails[1:]]
            self.garbage_add(self.garbage, mapped, garbage)
        return emails[0]
