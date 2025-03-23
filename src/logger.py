import logging
import os
from logging.handlers import RotatingFileHandler
from pathlib import Path


class LoggerWrapper():

    def __init__(self, logger_name: str = "standard_logger"):

        self.logger = logging.getLogger(logger_name)
        self.logger.setLevel(logging.DEBUG)
        self.setup_logger()

    def setup_logger(self):
        # Define and create folder
        logs_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'logs')
        Path(logs_folder).mkdir(parents=True, exist_ok=True)

        # Define file path
        log_file = log_file = os.path.join(logs_folder, 'predictify.log')

        # Setup File Handler
        handler = RotatingFileHandler(log_file, maxBytes=1000000, backupCount=5)
        handler.setLevel(logging.DEBUG)

        # Setup Console Handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.WARNING)

        # Setup Formatter
        formatter = logging.Formatter('%(asctime)s - [%(filename)s:%(lineno)d] - %(levelname)s - %(message)s')

        # Add Formatters to Handlers
        handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)

        # Add Handlers to Logger
        self.logger.addHandler(handler)
        self.logger.addHandler(console_handler)

    def info(self, message):
        self.logger.info(message)

    def debug(self, message):
        self.logger.debug(message)

    def warning(self, message):
        self.logger.warning(message)

    def error(self, message):
        self.logger.error(message)

    def critical(self, message):
        self.logger.critical(message)
        # Here we can add alerting/handling
