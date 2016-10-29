#!/usr/bin/env python

from distutils.core import setup

setup(
    name='Odoo ETL',
    version='0.1',
    description='Odoo ETL framework',
    author='Antonio Espinosa',
    author_email='antespi@gmail.com',
    url='https://github.com/antespi/odoo.etl',
    packages=['odooetl', 'odooetl.filters', 'odooetl.parsers'],
)
