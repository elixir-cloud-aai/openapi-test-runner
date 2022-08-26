"""Module unittests.test_test_runner.py

This module is to test the Test Runner class and its methods
"""

import json
import os
import unittest
from unittest.mock import (
    MagicMock,
    patch
)

from requests.models import Response
import yaml

from compliance_suite.exceptions.compliance_exception import (
    JobValidationException,
    TestFailureException
)
from compliance_suite.test_runner import TestRunner

YAML_SERVICE_INFO_SUCCESS = os.path.join(os.getcwd(), "unittests", "data", "tests", "success_service_info.yml")
JSON_SERVICE_INFO_SUCCESS = os.path.join(os.getcwd(), "unittests", "data", "json", "service_info_success.json")
JSON_SERVICE_INFO_FAILURE = os.path.join(os.getcwd(), "unittests", "data", "json", "service_info_failure.json")
YAML_CREATE_TASK_REQUEST_SUCCESS = os.path.join(os.getcwd(), "unittests", "data", "tests", "success_create_task.yml")
YAML_CREATE_TASK_REQUEST_FAILURE = os.path.join(os.getcwd(), "unittests", "data", "tests", "json_error_create_task.yml")


class TestTestRunner(unittest.TestCase):

    def test_validate_logic_success(self):
        """ Asserts validate_logic() function for successful schema validation to API Model"""

        with open(YAML_SERVICE_INFO_SUCCESS) as f:
            yaml_data = yaml.safe_load(f)

        test_runner = TestRunner(yaml_data["service"], yaml_data["server"], yaml_data["version"][0])
        test_runner.set_job_data(yaml_data["jobs"][0])
        test_runner.report_test = MagicMock()

        with open(JSON_SERVICE_INFO_SUCCESS) as f:
            json_data = json.load(f)
        test_runner.validate_logic(test_runner.job_data["name"], json_data, "Response")
        assert True

    def test_validate_logic_failure(self):
        """ Asserts validate_logic() function for unsuccessful schema validation to API Model"""

        with open(YAML_SERVICE_INFO_SUCCESS) as f:
            yaml_data = yaml.safe_load(f)

        test_runner = TestRunner(yaml_data["service"], yaml_data["server"], yaml_data["version"][0])
        test_runner.set_job_data(yaml_data["jobs"][0])
        test_runner.report_test = MagicMock()

        with open(JSON_SERVICE_INFO_FAILURE) as f:
            json_data = json.load(f)

        with self.assertRaises(TestFailureException):
            test_runner.validate_logic(test_runner.job_data["name"], json_data, "Response")

    def test_validate_request_body_success(self):
        """ Asserts validate_request_body() function for successful JSON format and schema validation to API Model"""

        with open(YAML_CREATE_TASK_REQUEST_SUCCESS) as f:
            yaml_data = yaml.safe_load(f)

        test_runner = TestRunner(yaml_data["service"], yaml_data["server"], yaml_data["version"][0])
        test_runner.set_job_data(yaml_data["jobs"][0])
        test_runner.report_test = MagicMock()
        test_runner.validate_request_body(yaml_data["jobs"][0]["request_body"])
        assert True

    def test_validate_request_body_failure(self):
        """ Asserts validate_request_body() function for unsuccessful JSON format"""
        with open(YAML_CREATE_TASK_REQUEST_FAILURE) as f:
            yaml_data = yaml.safe_load(f)

        test_runner = TestRunner(yaml_data["service"], yaml_data["server"], yaml_data["version"][0])
        test_runner.set_job_data(yaml_data["jobs"][0])
        test_runner.report_test = MagicMock()
        with self.assertRaises(JobValidationException):
            test_runner.validate_request_body(yaml_data["jobs"][0]["request_body"])

    @patch.object(TestRunner, "validate_logic")
    def test_validate_response_success(self, mock_validate_job):
        """ Asserts validate_response() function for successful response and schema validation to API Model"""

        mock_validate_job.return_value = {}
        with open(YAML_SERVICE_INFO_SUCCESS) as f:
            yaml_data = yaml.safe_load(f)

        test_runner = TestRunner(yaml_data["service"], yaml_data["server"], yaml_data["version"][0])
        test_runner.set_job_data(yaml_data["jobs"][0])
        test_runner.report_test = MagicMock()

        resp = Response()
        resp.status_code = 200
        test_runner.validate_response(resp)
        assert True

    def test_validate_response_failure(self):
        """ Asserts validate_response() function for unsuccessful response"""
        with open(YAML_SERVICE_INFO_SUCCESS) as f:
            yaml_data = yaml.safe_load(f)

        test_runner = TestRunner(yaml_data["service"], yaml_data["server"], yaml_data["version"][0])
        test_runner.set_job_data(yaml_data["jobs"][0])
        test_runner.report_test = MagicMock()

        resp = Response()
        resp.status_code = 400
        with self.assertRaises(TestFailureException):
            test_runner.validate_response(resp)
