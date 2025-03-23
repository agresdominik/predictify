import argparse
from time import sleep

from database_handler import Database
from gdpr_export import export_gdpr_data
from scraper import scrape_missing_infos, scraping

db = Database()

# Initialize the parser
parser = argparse.ArgumentParser(description="A python script written in Python3.13 which continuously checks what spotify songs "
                                             "the user is listening to and logging these in a local database. \n"
                                             "The Script also has a export function where it can read out the gdpr data exported by the user.")

# Add optional arguments
parser.add_argument('--verbose', '-v', action='store_true', help="Enable verbose output")
parser.add_argument('--export', '-e', action='store_true', help="Export the gdpr data from spotify if not done already")

# Parse the arguments
args = parser.parse_args()

if args.verbose:
    print('Enabled verbose mode')
    # implement logger

if args.export:
    print('Scraping GDPR Data')
    # The next function can gat a int witch defines the amount of songs witch will be scraped from the gdpr files.
    # e.g. if 500 is input, the last 500 played songs will come up, if left empty, the last 100.
    export_gdpr_data()
    scrape_missing_infos()

while True:
    print('Scraping API...')
    scraping()
    print('Done Scraping')
    sleep(1800)


# TODO: Trap this:
db.close()
