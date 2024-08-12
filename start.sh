#!/bin/sh

set -eu

python3 -m venv --upgrade-deps .venv
.venv/bin/python3 -m pip install -r requirements.txt
.venv/bin/python3  main.py
