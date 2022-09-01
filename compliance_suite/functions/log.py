"""Module compliance_suite.functions.log.py

This module contains the logging utility functions to define the logger and log the colored messages in console
"""

import logging

import colorlog

from compliance_suite.constants.constants import LOGGING_LEVEL


def set_logging():
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
logger = logging.getLogger(__name__)
logger.addHandler(set_logging())
logger.setLevel(logging.DEBUG)  # Define the log level for the compliance suite
