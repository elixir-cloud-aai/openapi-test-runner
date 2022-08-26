"""Module compliance_suite.functions.log.py

This module contains the print utility functions to print colored messages in console
"""

import logging

import colorlog

from compliance_suite.constants.constants import LOGGING_LEVEL


def set_logging():

    logging.addLevelName(LOGGING_LEVEL['SKIP'], 'SKIP')
    logging.addLevelName(LOGGING_LEVEL['SUCCESS'], 'SUCCESS')
    logging.addLevelName(LOGGING_LEVEL['SUMMARY'], 'SUMMARY')
    formatter = colorlog.ColoredFormatter(
        "%(log_color)s%(message)s",
        log_colors={'SKIP': 'blue', 'SUCCESS': 'green', 'SUMMARY': 'yellow', 'DEBUG': 'white',
                    'INFO': 'white', 'ERROR': 'red'}
    )
    handler = logging.StreamHandler()
    handler.setFormatter(formatter)
    return handler


logger = logging.getLogger(__name__)
logger.addHandler(set_logging())
logger.setLevel(logging.DEBUG)
