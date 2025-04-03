import argparse
import atexit
import os
import sys
import traceback
from time import sleep

from database_handler import Database
from gdpr_export import export_gdpr_data
from logger import LoggerWrapper
from scraper import scrape_missing_infos, scraping

log = LoggerWrapper()


def _handle_exit():
    """
    Function to log exit information if the script ends unexpectedly.
    """
    log.critical("Script terminated unexpectedly.")


def _log_crash_info(exc_type, exc_value, exc_tb):
    """Custom function to log crash info when an exception occurs."""
    log.critical("A critical error occurred!", exc_info=(exc_type, exc_value, exc_tb))
    log.critical("Exception type: %s", exc_type)
    log.critical("Exception message: %s", exc_value)
    log.critical("Stack trace:\n%s", ''.join(traceback.format_tb(exc_tb)))


# Register the exit handler and excepthook
atexit.register(_handle_exit)
sys.excepthook = _log_crash_info


# Initialize the parser
parser = argparse.ArgumentParser(description="A python script written in Python3.13 which continuously checks what spotify songs "
                                             "the user is listening to and logging these in a local database. \n"
                                             "The Script also has a export function where it can read out the gdpr data exported by the user.")

# Add optional arguments
parser.add_argument('--verbose', '-v', action='store_true', help="Enable verbose output")
parser.add_argument('--export', type=str, choices=['TEST', 'PRODUCTION'], required=True,
                    help="Export the gdpr data from spotify if not done already. Choose between TEST and PRODUCTION."
                    "TEST will export only a small number of songs, PRODUCTION will export all songs.")

# Parse the arguments
args = parser.parse_args()

if args.verbose:
    log.set_console_handler_to_debug()
    log.info('Enabled verbose mode')

db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'data', f'spotify_scrape_{args.export}.db')

if args.export == 'TEST':
    export_size = 10000
    log.info(f'Scraping GDPR Data. Sample size: {export_size}')
    db = Database(db_path)
    export_gdpr_data(db, export_size)
    scrape_missing_infos(db)
elif args.export == 'PRODUCTION':
    export_size = 1000000
    log.info('Scraping all GDPR Data.')
    db = Database(db_path)
    export_gdpr_data(db, export_size)
    scrape_missing_infos(db)
else:
    raise ValueError('Invalid export type. Please choose between TEST and PRODUCTION.')

while True:
    log.info('Scraping API...')
    scraping(db)
    log.info('Done scraping API. Sleeping for 30 minutes...')
    sleep(1800)
