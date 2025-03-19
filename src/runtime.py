from time import sleep

from scraper import scraping

# Run forever on intervals of 30 minutes
while True:
    scraping()
    sleep(1800)
