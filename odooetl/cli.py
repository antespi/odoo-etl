# -*- coding: utf-8 -*-
# Copyright 2016 Antonio Espinosa (http://github.com/antespi)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import sys
import traceback
import argparse
import logging
try:
    import odoo
except:
    try:
        import openerp as odoo
    except:
        odoo = None
from . import tools

_logger = logging.getLogger(__name__)


def _log_level_init(log_level):
    if odoo:
        odoo.netsvc.init_logger()


def _log_level_set(log_level):
    logging.getLogger('').setLevel(log_level)


class CliApplication(object):
    options = {}
    args = {}
    config = {}

    def __init__(self, name=None, description=None, version="0.1",
                 log_level=logging.INFO):
        _log_level_init(log_level)
        self.argp = argparse.ArgumentParser(
            prog=name, description=description)
        version = '%(prog)s ' + '%s' % version
        self.argp.add_argument('--version', action='version', version=version)
        self.argp.add_argument(
            '-d', '--dry-run', action='store_true', default=False,
            help="Don't perform any create/write/delete operation")
        self.argp.add_argument('-v', '--verbose', type=int)
        self.argp.add_argument(
            '-c', '--config', metavar='CONFIG', type=tools.config_read,
            required=True,
            help="YAML Config file for loading Odoo environment, parser "
                 "options, ...")

    def options_read(self):
        opts = tools.getmethod(self.etl, 'options_add')
        if opts:
            opts(self.argp)
        self.options, self.args = self.argp.parse_known_args()
        self.etl.options = self.options
        self.etl.args = self.args

    def _verbose_load(self):
        levels = [
            logging.CRITICAL,  # -v0
            logging.ERROR,     # -v1
            logging.WARNING,   # -v2
            logging.INFO,      # -v3
            logging.DEBUG,     # -v4
        ]
        if 'verbose' in self.options:
            verbose = self.options.verbose if self.options.verbose > 0 else 0
            if verbose >= len(levels):
                verbose = len(levels) - 1
            _log_level_set(levels[verbose])

    def load(self):
        self._verbose_load()
        load = tools.getmethod(self.etl, 'load')
        if load:
            load()
        return True

    def norun(self):
        _logger.error("This etl has no 'run' method")

    def nocleanup(self):
        pass

    def run(self, etl):
        self.etl = etl
        try:
            self.options_read()
            self.load()
        except Exception as e:
            _logger.error('Exception: %s' % e)
            _logger.debug('Traceback: %s' % traceback.format_exc())
            sys.exit(1)
        run = tools.getmethod(self.etl, 'run') or self.norun
        cleanup = tools.getmethod(self.etl, 'cleanup') or self.nocleanup
        try:
            run()
        except KeyboardInterrupt:
            _logger.info('Stopped by user')
        except Exception as e:
            _logger.error('Exception: %s' % e)
            _logger.debug('Traceback: %s' % traceback.format_exc())
            sys.exit(2)
        finally:
            cleanup()
