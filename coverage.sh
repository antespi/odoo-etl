#!/bin/bash

nosetests --with-coverage \
          --cover-html \
          --cover-package=odooetl \
          --cover-inclusive
