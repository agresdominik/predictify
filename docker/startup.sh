#!/bin/sh
#
# Startup predictify. Don't use this. This is for docker specifically.
source .venv/bin/activate
.venv/bin/python src/runtime.py
