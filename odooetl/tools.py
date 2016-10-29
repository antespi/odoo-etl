# -*- coding: utf-8 -*-
# Copyright 2016 Antonio Espinosa (http://github.com/antespi)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import os
import collections
import yaml


def getmethod(obj, method, default=None):
    if obj and getattr(obj, method, None):
        method = getattr(obj, method)
        if hasattr(method, '__call__'):
            return method
    return default


# http://stackoverflow.com/a/3233356/2868531
def dict_recursive_update(d, u):
    for k, v in u.iteritems():
        if isinstance(v, collections.Mapping):
            r = dict_recursive_update(d.get(k, {}), v)
            d[k] = r
        else:
            d[k] = u[k]
    return d


def config_read(filename):
    if not os.path.exists(filename):
        raise IOError("Config file '%s' does not exist." % filename)
    with open(filename) as pf:
        config = yaml.load(pf.read())
    return config


def config_get(config, path, default=None):
    value = default
    if path:
        parts = path.split('.')
        value = config or {}
        for part in parts:
            if part in value:
                value = value[part]
            else:
                return default
    return value


# http://stackoverflow.com/a/480227/2868531
# https://www.peterbe.com/plog/uniqifiers-benchmark
def uniquify(seq):
    seen = set()
    seen_add = seen.add
    return [x for x in seq if not (x in seen or seen_add(x))]
