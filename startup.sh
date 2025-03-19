#!/bin/sh
#
# Starup the predictify scraper

if test -f ./requirements.txt 
then
    pip install -r ./requirements.txt
else 
    printf "Missing requirements file! aborting...\n"
    exit 1
fi

python3 ./src/scraper.py

