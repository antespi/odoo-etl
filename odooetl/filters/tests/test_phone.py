# -*- coding: utf-8 -*-
# Copyright 2016 Antonio Espinosa (http://github.com/antespi)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from unittest import TestCase
from odooetl.filters import FilterPhone


class TestPhone(TestCase):

    def test_valid(self):
        cases = {
            # International
            '+34 911 23 12 12': (None, '(+34) 91 123 12 12'),
            '+44 1708 123456': (None, '+44 (0) 1708-123-456'),
            # Spain
            '+34 911 23 12 13': ('es', '91.123 12 13'),
            '+34 927 12 12 12': ('Es', '927 121 212'),
            '+34 900 123 123': ('ES', '900-123-123'),
            '+34 902 12 31 23': ('ES', '902 123 123'),
            '+34 800 123 123': ('ES', '800 123 123'),
            '+34 636 12 31 23': ('es_ES', '636.123.123'),
            # United Kingdom
            '+44 1708 123457': ('UK', '1708 123 457'),
            '+44 842 123 1234': ('uk', '(0842) 123 1234'),
            '+44 20 1234 1234': ('gb', '020 1234 1234'),
            '+44 331 123 1234': ('Gb', '0331-123-1234'),
            '+44 800 123456': ('GB_en', '0800.123456'),
        }
        for result, value in cases.iteritems():
            self.assertEqual(result, FilterPhone(
                config={'country_code_default': value[0]}).apply(value[1]))

    # def test_invalid(self):
    #     cases = ['contact+example.org', 'Contact', '', '  @example.org',
    #              'contact@  ', 0, 1, 5, [], {}, (), False, None, ]
    #     for value in cases:
    #         self.assertFalse(FilterEmail().apply(value))

    # def test_map(self):
    #     item = {
    #         'f1': 'contact@example.org',
    #         'f2': '@example.org',
    #         'f3': 'Name Lastname <other@example.org>'
    #     }
    #     result = {
    #         'f1': 'contact@example.org',
    #         'f2': False,
    #         'f3': 'other@example.org',
    #     }
    #     mapped = {}
    #     for field in item.keys():
    #         mapped = FilterEmail(
    #             fields=field, config={'garbage': False}).map(item)
    #     self.assertTrue(result, mapped)

    # def test_multi(self):
    #     item_valid = {
    #         'f1': ' contact@example.org',
    #         'f2': 'other@example.org ',
    #     }
    #     item_invalid = {
    #         'f1': '@example.org',
    #         'f2': 'other@example.org',
    #     }
    #     item_mix = {
    #         'f1': '@example.org,contact@example.org',
    #         'f2': 'other@example.org',
    #     }
    #     f = FilterEmail(fields=['f1', 'f2'], config={'separator': ','})
    #     self.assertEqual(False, f.map({}))
    #     mapped = {}
    #     self.assertEqual('contact@example.org', f.map(item_valid, mapped))
    #     self.assertEqual('Email: other@example.org', mapped.get('_garbage'))
    #     mapped = {}
    #     self.assertEqual('other@example.org', f.map(item_invalid, mapped))
    #     self.assertEqual('Bad email: @example.org', mapped.get('_garbage'))
    #     mapped = {}
    #     self.assertEqual('contact@example.org', f.map(item_mix, mapped))
    #     self.assertEqual(
    #         'Bad email: @example.org - Email: other@example.org',
    #         mapped.get('_garbage'))
