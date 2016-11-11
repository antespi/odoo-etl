# -*- coding: utf-8 -*-
# Copyright 2016 Antonio Espinosa (http://github.com/antespi)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import datetime
import time
from .base import (
    BaseFilter, timezone_set, timezone_get)
from .stringify import FilterStringify


class FilterTimestamp(BaseFilter):
    modules = {
        'date': datetime.date.fromtimestamp,
        'datetime': datetime.datetime.fromtimestamp,
        'time': time.localtime,
    }

    def __init__(self, fields=None, default=False, config={}):
        # type: date, time, timestamp, struct_time
        super(FilterTimestamp, self).__init__(
            fields=fields, default=default, config=config)
        self.type = self.config.get('type', 'timestamp')
        self.ifmt = self.config.get('ifmt', False)
        self.ofmt = self.config.get('ofmt', False)
        self.offset = self.config.get('offset', 0)
        self.utc = self.config.get('utc', True)
        self.tz = self.config.get('tz', 'UTC')
        self.current_tz = timezone_get(default='UTC')

    def _timestamp_get(self, value):
        f = FilterStringify(default=False, config=self.config)
        timestamp = f.apply(value)
        if self.ifmt:
            ifmt = self.ifmt
            if not value:
                return None
            if not isinstance(ifmt, (list, tuple)):
                ifmt = [ifmt]
            for format in ifmt:
                try:
                    t = time.strptime(timestamp, format)
                    break
                except:
                    t = False
            timestamp = time.mktime(t) if t else False
        if not timestamp:
            return None
        try:
            timestamp = float(timestamp)
        except:
            return None
        return timestamp

    def _timestamp_convert(self, timestamp):
        if self.offset:
            timestamp = timestamp + self.offset
        if self.utc:
            timestamp = int(time.mktime(time.gmtime(timestamp)))
        return timestamp

    def _timestamp_output(self, timestamp):
        value = timestamp
        module = self.modules.get(self.type, None)
        if self.ofmt:
            value = time.strftime(self.ofmt, time.localtime(timestamp))
        elif module:
            value = module(timestamp)
        return value

    def apply(self, value):
        if self.tz:
            timezone_set(self.tz)
        timestamp = self._timestamp_get(value)
        if timestamp is None:
            return self.default
        value = self._timestamp_output(self._timestamp_convert(timestamp))
        if self.tz:
            timezone_set(self.current_tz)
        return value

    def map(self, item, mapped={}):
        f = FilterStringify(
            fields=self.fields, default=False, config=self.config)
        value = f.map(item, mapped=mapped)
        return self.apply(value)


class FilterDate(FilterTimestamp):

    def __init__(self, fields=None, default=0, config={}):
        config = config or {}
        config['type'] = 'date'
        super(FilterDate, self).__init__(
            fields=fields, default=default, config=config)


class FilterDatetime(FilterTimestamp):

    def __init__(self, fields=None, default=0., config={}):
        config = config or {}
        config['type'] = 'datetime'
        super(FilterDatetime, self).__init__(
            fields=fields, default=default, config=config)


class FilterTime(FilterTimestamp):

    def __init__(self, fields=None, default=0., config={}):
        config = config or {}
        config['type'] = 'time'
        super(FilterTime, self).__init__(
            fields=fields, default=default, config=config)
