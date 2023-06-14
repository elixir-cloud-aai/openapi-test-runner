"""Module unittests.functions.test_log.py

This module tests the log.py file
"""

import logging
import unittest.mock

import pytest

from compliance_suite.constants.constants import (
    LOGGING_LEVEL,
    PATTERN_HASH_CENTERED
)
from compliance_suite.functions.log import CustomLogger


class TestLog:

    @pytest.fixture
    def logger(self):
        """Pytest fixture to setup the logger"""

        logger = CustomLogger(__name__)
        logger.addHandler(CustomLogger.set_logging())
        logger.setLevel(logging.DEBUG)
        return logger

    def test_skip(self, logger):
        """Test that the skip method logs a message with the SKIP level."""

        logger.log = unittest.mock.MagicMock()
        logger.skip("This is skip message")
        logger.log.assert_called_once_with(LOGGING_LEVEL['SKIP'], "This is skip message")

    def test_success(self, logger):
        """Test that the success method logs a message with the SUCCESS level."""

        logger.log = unittest.mock.MagicMock()
        logger.success("This is successful message")
        logger.log.assert_called_once_with(LOGGING_LEVEL['SUCCESS'], "This is successful message")

    def test_summary(self, logger):
        """Test that the summary method logs a message with the SUMMARY level."""

        logger.log = unittest.mock.MagicMock()
        pattern_hash_center_pad_30: str = "{:#^30}"
        logger.summary("This is summary message", pattern_hash_center_pad_30)
        logger.log.assert_called_once_with(LOGGING_LEVEL['SUMMARY'], "###This is summary message####")
