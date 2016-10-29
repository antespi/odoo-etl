#!/bin/bash

flake8 odooetl \
       --isolate  \
       --exclude __init__.py \
       --max-complexity 15
