"""Module compliance_suite.exceptions.compliance_exception.py

This module contains class definition for compliance exceptions.
"""

from typing import Any


class BasicException(Exception):
    """ Base Exception Class for all custom exceptions """

    def __init__(self, name: str, message: str, details: Any, _type: str):
        self.name = name
        self.message = message
        self.details = details
        self.type = _type

        super().__init__(f"Exception Name - {self.name}. Type - {self.type}. Message - {self.message}. "
                         f"Details - {self.details}")


class TestFailureException(BasicException):
    """ When a test fails due to incomplete/wrong implementation of a TES server. The exception
    highlights the possible changes required by the TES server to follow the standard
    TES API Specs"""

    def __init__(self, name: str, message: str, details: Any):
        BasicException.__init__(self, name=name, message=message, details=details,
                                _type="TestFailureException")


class JobValidationException(BasicException):
    """ If the provided test file is not valid, this exception is raised. Test files should follow the
    Test Template and schema to resolve this"""

    def __init__(self, name: str, message: str, details: Any):
        BasicException.__init__(self, name=name, message=message, details=details,
                                _type="JobValidationException")


class TestRunnerException(BasicException):
    """ Exception raised within the Test runner. See the error details for more info """

    def __init__(self, name: str, message: str, details: Any):
        BasicException.__init__(self, name=name, message=message, details=details,
                                _type="TestRunnerException")
