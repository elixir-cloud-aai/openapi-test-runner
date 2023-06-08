"""Module compliance_suite.functions.log.py

This module contains the logging utility functions to define the logger and log the colored messages in console
"""

import logging

import colorlog

from compliance_suite.constants.constants import LOGGING_LEVEL


class CustomLogger(logging.Logger):
    """CustomLogger extends the base Logger class from the logging module to provide additional logging
    functionality.
    """

    def __init__(self, name: str, level=logging.NOTSET):
        """Initializes an instance of CustomLogger.

        Args:
            name: The name of the logger.
            level: The logging level for the logger. Defaults to logging.NOTSET.
        """
        super().__init__(name, level)

    def skip(self, message: str):
        """Logs a message with the additional logging level SKIP.

        Args:
            message: The message to be logged.
        """
        self.log(LOGGING_LEVEL['SKIP'], message)

    def success(self, message: str):
        """Logs a message with the additional logging level SUCCESS.

        Args:
            message: The message to be logged.
        """
        self.log(LOGGING_LEVEL['SUCCESS'], message)

    def summary(self, message: str):
        """Logs a message with the additional logging level SUMMARY.

        Args:
            message: The message to be logged.
        """
        self.log(LOGGING_LEVEL['SUMMARY'], message)

    @staticmethod
    def set_logging() -> logging.StreamHandler:
        """Set the logging for the compliance suite. Uses colorlog library to display colored logs"""

        # Add custom levels
        logging.addLevelName(LOGGING_LEVEL['SKIP'], 'SKIP')
        logging.addLevelName(LOGGING_LEVEL['SUCCESS'], 'SUCCESS')
        logging.addLevelName(LOGGING_LEVEL['SUMMARY'], 'SUMMARY')

        # Define the log properties
        formatter = colorlog.ColoredFormatter(
            "%(log_color)s%(message)s",
            log_colors={'SKIP': 'blue', 'SUCCESS': 'green', 'SUMMARY': 'yellow', 'DEBUG': 'white',
                        'INFO': 'white', 'ERROR': 'red'}
        )
        handler = logging.StreamHandler()
        handler.setFormatter(formatter)
        return handler


# Set the logger
logger = CustomLogger(__name__)
logger.addHandler(CustomLogger.set_logging())
logger.setLevel(logging.DEBUG)  # Define the log level for the compliance suite
