# -*- coding: utf-8 -*-
# Copyright 2016 Antonio Espinosa (http://github.com/antespi)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import time
import datetime
from unittest import TestCase
from odooetl.filters import (
    FilterTimestamp, FilterDate, FilterDatetime, FilterTime,
    datetime_to_string)


class TestDate(TestCase):

    def test_timestamp(self):
        # 1478443666.78678 => '2016-11-06 14:47:46' UTC
        f = FilterTimestamp()
        self.assertEqual(1478443666, f.apply(1478443666.78678))
        self.assertEqual(1478443666, f.apply('1478443666.78678'))
        f = FilterTimestamp(config={'ifmt': '%Y-%m-%d %H:%M:%S'})
        self.assertEqual(1478443666, f.apply('2016-11-06 14:47:46'))
        f = FilterTimestamp(config={
            'ifmt': '%Y-%m-%d %H:%M:%S',
            'tz': 'Europe/Madrid',
            'utc': False,
        })
        self.assertEqual(1478443666, f.apply('2016-11-06 15:47:46'))
        f = FilterTimestamp(config={
            'ifmt': '%Y-%m-%d %H:%M:%S',
            'ofmt': '%Y-%m-%d %H:%M:%S',
            'tz': 'Europe/Madrid',
            'utc': True,
        })
        self.assertEqual('2016-11-06 14:47:46', f.apply('2016-11-06 15:47:46'))

    def test_datetime(self):
        # 1478443666.78678 => '2016-11-06 14:47:46' UTC
        f = FilterDatetime(config={
            'ifmt': '%Y-%m-%d %H:%M:%S',
            'tz': 'Europe/Madrid',
            'utc': True,
        })
        self.assertEqual(
            datetime.datetime(2016, 11, 6, 14, 47, 46),
            f.apply('2016-11-06 15:47:46'))
        f = FilterDatetime(config={
            'ifmt': '%Y-%m-%d %H:%M:%S',
            'tz': 'Europe/Madrid',
            'utc': False,
        })
        self.assertEqual(
            datetime.datetime(2016, 11, 6, 15, 47, 46),
            f.apply('2016-11-06 15:47:46'))

    def test_date(self):
        # 1478390400 => '2016-11-06 00:00:00' UTC
        f = FilterDate(config={
            'ifmt': '%Y-%m-%d',
        })
        self.assertEqual(datetime.date(2016, 11, 6), f.apply('2016-11-06'))
        f = FilterDate()
        self.assertEqual(datetime.date(2016, 11, 6), f.apply('1478390400'))
        self.assertEqual(datetime.date(2016, 11, 6), f.apply('1478390420'))
        self.assertEqual(datetime.date(2016, 11, 6), f.apply('1478400420'))
        self.assertEqual(datetime.date(2016, 11, 5), f.apply('1478390399'))

    def test_time(self):
        # 1478443666.78678 => '2016-11-06 14:47:46' UTC
        f = FilterTime(config={
            'ifmt': '%Y-%m-%d %H:%M:%S',
        })
        self.assertEqual(
            time.gmtime(1478443666), f.apply('2016-11-06 14:47:46'))

    def test_datetime_to_string(self):
        self.assertEqual(
            '2016-11-06',
            datetime_to_string(datetime.date(2016, 11, 6), '%Y-%m-%d'))
        self.assertEqual(
            '2016-11-06',
            datetime_to_string(time.gmtime(1478390400), '%Y-%m-%d'))
        self.assertEqual(
            '2016-11-06', datetime_to_string('2016-11-06', '%Y-%m-%d'))
        self.assertEqual('', datetime_to_string(None, '%Y-%m-%d'))

    def test_ifmt(self):
        # 1478443666.78678 => '2016-11-06 14:47:46' UTC
        f = FilterDate(config={
            'ifmt': ['%Y-%m-%d %H:%M:%S', '%Y-%m-%d'],
        })
        self.assertEqual(datetime.date(2016, 11, 6), f.apply('2016-11-06'))
        self.assertEqual(datetime.date(2016, 11, 6),
                         f.apply('2016-11-06 10:11:12'))
        self.assertEqual(False, f.apply('1478390400'))
        self.assertEqual(False, f.apply(1478390400))
        self.assertEqual(False, f.apply('06/11/2016'))
        f = FilterDate(config={
            'ifmt': ['%Y-%m-%d %H:%M:%S', '%Y-%m-%d', '%d/%m/%Y'],
        })
        self.assertEqual(datetime.date(2016, 11, 6), f.apply('06/11/2016'))

    def test_ofmt(self):
        # 1478443666.78678 => '2016-11-06 14:47:46' UTC
        f = FilterTimestamp(config={
            'ofmt': '%Y-%m-%d %H:%M:%S',
        })
        self.assertEqual('2016-11-06 14:47:46', f.apply(1478443666))
        f = FilterTimestamp(config={
            'ofmt': '%Y-%m-%d',
        })
        self.assertEqual('2016-11-06', f.apply(1478443666))
        f = FilterTimestamp(config={
            'ofmt': '%d/%m/%Y',
        })
        self.assertEqual('06/11/2016', f.apply(1478443666))

    def test_offset(self):
        # 1478443666.78678 => '2016-11-06 14:47:46' UTC
        f = FilterTimestamp(config={
            'offset': 3600,
            'ofmt': '%Y-%m-%d %H:%M:%S',
        })
        self.assertEqual('2016-11-06 15:47:46', f.apply(1478443666))

    def test_map(self):
        item = {
            'f1': 1478443666,
            'f2': '1478443666',
        }
        result = {
            'f1': '2016-11-06 15:47:46',
            'f2': '2016-11-06 15:47:46',
        }
        mapped = {}
        for field in item.keys():
            mapped = FilterTimestamp(
                fields=field, config={'ofmt': '%Y-%m-%d %H:%M:%S'}).map(item)
        self.assertTrue(result, mapped)
