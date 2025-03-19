#!/bin/sh
#
# Starup the predictify scraper

if test -f ./requirements.txt 
then
    python3 -m venv .venv
    .venv/bin/pip install -r ./requirements.txt
else 
    printf "Missing requirements file! aborting...\n"
    exit 1
fi

.venv/bin/python3 src/scraper.py
