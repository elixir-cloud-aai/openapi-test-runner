"""Module unittests.test_test_runner.py

This module is to test the Test Runner class and its methods
"""

import unittest
from unittest.mock import (
    MagicMock,
    patch
)

from compliance_suite.exceptions.compliance_exception import (
    JobValidationException,
    TestFailureException
)
from compliance_suite.functions.client import Client
from compliance_suite.test_runner import TestRunner


class TestTestRunner(unittest.TestCase):

    def test_validate_logic_success(self):
        """ Asserts validate_logic() function for successful schema validation to API Model"""

        test_runner = TestRunner("test", "test", "v1.0")
        test_runner.set_job_data(
            {
                "operation": "test",
                "endpoint": "test"
            }
        )
        test_runner.report_test = MagicMock()

        service_info_response = {
            "id": "test",
            "name": "test",
            "type": {
                "group": "org.ga4gh",
                "artifact": "tes",
                "version": "1.0"
            },
            "organization": {"name": "test", "url": "https://example.com"},
            "version": "test"
        }

        test_runner.validate_logic("service_info", service_info_response, "Response")

        assert True

    def test_validate_logic_failure(self):
        """ Asserts validate_logic() function for unsuccessful schema validation to API Model"""

        test_runner = TestRunner("test", "test", "v1.0")
        test_runner.set_job_data(
            {
                "operation": "test",
                "endpoint": "test"
            }
        )
        test_runner.report_test = MagicMock()
        with self.assertRaises(TestFailureException):
            test_runner.validate_logic("service_info", {}, "Response")

    @patch.object(TestRunner, "validate_logic")
    def test_validate_request_body_success(self, mock_validate_job):
        """ Asserts validate_request_body() function for successful JSON format and schema validation to API Model"""

        mock_validate_job.return_value = {}

        test_runner = TestRunner("test", "test", "v1.0")
        test_runner.set_job_data(
            {
                "name": "test",
                "operation": "test",
                "endpoint": "test"
            }
        )
        test_runner.report_test = MagicMock()
        test_runner.validate_request_body("{}")
        assert True

    def test_validate_request_body_failure(self):
        """ Asserts validate_request_body() function for unsuccessful JSON format"""

        test_runner = TestRunner("test", "test", "v1.0")
        test_runner.set_job_data(
            {
                "operation": "test",
                "endpoint": "test"
            }
        )
        test_runner.report_test = MagicMock()
        with self.assertRaises(JobValidationException):
            test_runner.validate_request_body("{")

    @patch.object(TestRunner, "validate_logic")
    def test_validate_response_success_get(self, mock_validate_job):
        """ Asserts validate_response() function for successful response and schema validation to API Model"""

        mock_validate_job.return_value = {}

        test_runner = TestRunner("test", "test", "v1.0")
        test_runner.set_job_data(
            {
                "name": "list_tasks",
                "operation": "test",
                "endpoint": "test",
                "query_parameters": [{"view": "BASIC"}],
                "response": {"200": ""}
            }
        )
        test_runner.report_test = MagicMock()

        resp = MagicMock(status_code=200, text="")
        test_runner.validate_response(resp)
        assert True

    @patch.object(TestRunner, "validate_logic")
    def test_validate_response_success(self, mock_validate_job):
        """ Asserts validate_response() function for successful response and schema validation to API Model"""

        mock_validate_job.return_value = {}

        test_runner = TestRunner("test", "test", "v1.0")
        test_runner.set_job_data(
            {
                "name": "test",
                "operation": "test",
                "endpoint": "test",
                "response": {"200": ""}
            }
        )
        test_runner.report_test = MagicMock()

        resp = MagicMock(status_code=200)
        test_runner.validate_response(resp)
        assert True

    def test_validate_response_failure(self):
        """ Asserts validate_response() function for unsuccessful response"""

        test_runner = TestRunner("test", "test", "v1.0")
        test_runner.set_job_data(
            {
                "operation": "test",
                "endpoint": "test",
                "response": {"200": ""}
            }
        )
        test_runner.report_test = MagicMock()

        resp = MagicMock(status_code=400)
        with self.assertRaises(TestFailureException):
            test_runner.validate_response(resp)

    @patch.object(Client, "poll_request")
    @patch.object(TestRunner, "validate_response")
    def test_run_jobs_get_task(self, mock_validate_response, mock_client):
        """Assert the run job method for get task to be successful"""

        mock_validate_response.return_value = {}
        mock_client.return_value = MagicMock()

        test_runner = TestRunner("TES", "test", "1.0.0")
        job_data = {
            "name": "get_task",
            "description": "test",
            "operation": "test",
            "endpoint": "test",
            "query_parameters": [{"view": "BASIC"}],
            "polling": {"interval": 10, "timeout": 10},
            "env_vars": {
                "check_cancel": "True"
            }
        }
        test_runner.set_auxiliary_space("id", "1234")
        test_runner.run_tests(job_data, MagicMock())

        assert True

    @patch.object(Client, "send_request")
    @patch.object(TestRunner, "validate_request_body")
    @patch.object(TestRunner, "validate_logic")
    def test_run_jobs_create_task(self, mock_validate_logic, mock_validate_request_body, mock_client):
        """Assert the run job method for create task to be successful"""

        mock_validate_logic.return_value = {}
        mock_validate_request_body.return_value = {}
        resp = MagicMock(status_code=200, text='{"id": "1234"}')
        mock_client.return_value = resp

        test_runner = TestRunner("TES", "test", "1.0.0")
        job_data = {
            "name": "create_task",
            "description": "test",
            "operation": "test",
            "endpoint": "test",
            "request_body": "{}",
            "storage_vars": {
                "id": "$response.id"
            },
            "response": {"200": ""}
        }
        test_runner.run_tests(job_data, MagicMock())

        assert True
