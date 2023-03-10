"""Module unittests.test_test_runner.py

This module is to test the Test Runner class and its methods
"""

from unittest.mock import (
    MagicMock,
    patch
)

import pytest

from compliance_suite.exceptions.compliance_exception import (
    JobValidationException,
    TestFailureException
)
from compliance_suite.functions.client import Client
from compliance_suite.test_runner import TestRunner


TEST_VERSIONS = ["1.0.0", "1.1.0"]


class TestTestRunner:

    @pytest.mark.parametrize("version", TEST_VERSIONS)
    def test_validate_logic_success(self, version):
        """ Asserts validate_logic() function for successful schema validation to API Model"""

        test_runner = TestRunner("test", "test", version)
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

        assert test_runner.validate_logic("service_info", service_info_response, "Response") is None

    @pytest.mark.parametrize("version", TEST_VERSIONS)
    def test_validate_logic_failure(self, version):
        """ Asserts validate_logic() function for unsuccessful schema validation to API Model"""

        test_runner = TestRunner("test", "test", version)
        test_runner.set_job_data(
            {
                "operation": "test",
                "endpoint": "test"
            }
        )
        test_runner.report_test = MagicMock()
        with pytest.raises(TestFailureException):
            test_runner.validate_logic("service_info", {}, "Response")

    @pytest.mark.parametrize("version", TEST_VERSIONS)
    @patch.object(TestRunner, "validate_logic")
    def test_validate_request_body_success(self, mock_validate_job, version):
        """ Asserts validate_request_body() function for successful JSON format and schema validation to API Model"""

        mock_validate_job.return_value = {}

        test_runner = TestRunner("test", "test", version)
        test_runner.set_job_data(
            {
                "name": "test",
                "operation": "test",
                "endpoint": "test"
            }
        )
        test_runner.report_test = MagicMock()
        assert test_runner.validate_request_body("{}") is None

    @pytest.mark.parametrize("version", TEST_VERSIONS)
    def test_validate_request_body_failure(self, version):
        """ Asserts validate_request_body() function for unsuccessful JSON format"""

        test_runner = TestRunner("test", "test", version)
        test_runner.set_job_data(
            {
                "operation": "test",
                "endpoint": "test"
            }
        )
        test_runner.report_test = MagicMock()
        with pytest.raises(JobValidationException):
            test_runner.validate_request_body("{")

    @pytest.mark.parametrize("version", TEST_VERSIONS)
    @patch.object(TestRunner, "validate_logic")
    def test_validate_response_success_get(self, mock_validate_job, version):
        """ Asserts validate_response() function for successful response and schema validation to API Model"""

        mock_validate_job.return_value = {}

        test_runner = TestRunner("test", "test", version)
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
        assert test_runner.validate_response(resp) is None

    @pytest.mark.parametrize("version", TEST_VERSIONS)
    @patch.object(TestRunner, "validate_logic")
    def test_validate_response_success(self, mock_validate_job, version):
        """ Asserts validate_response() function for successful response and schema validation to API Model"""

        mock_validate_job.return_value = {}

        test_runner = TestRunner("test", "test", version)
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
        assert test_runner.validate_response(resp) is None

    @pytest.mark.parametrize("version", TEST_VERSIONS)
    def test_validate_response_failure(self, version):
        """ Asserts validate_response() function for unsuccessful response"""

        test_runner = TestRunner("test", "test", version)
        test_runner.set_job_data(
            {
                "operation": "test",
                "endpoint": "test",
                "response": {"200": ""}
            }
        )
        test_runner.report_test = MagicMock()

        resp = MagicMock(status_code=400)
        with pytest.raises(TestFailureException):
            test_runner.validate_response(resp)

    @pytest.mark.parametrize("version", TEST_VERSIONS)
    @patch.object(Client, "poll_request")
    @patch.object(TestRunner, "validate_response")
    def test_run_jobs_get_task(self, mock_validate_response, mock_client, version):
        """Assert the run job method for get task to be successful"""

        mock_validate_response.return_value = {}
        mock_client.return_value = MagicMock()

        test_runner = TestRunner("test", "test", version)
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
        assert test_runner.run_tests(job_data, MagicMock()) is None

    @pytest.mark.parametrize("version", TEST_VERSIONS)
    @patch.object(Client, "send_request")
    @patch.object(TestRunner, "validate_request_body")
    @patch.object(TestRunner, "validate_logic")
    def test_run_jobs_create_task(self, mock_validate_logic, mock_validate_request_body, mock_client, version):
        """Assert the run job method for create task to be successful"""

        mock_validate_logic.return_value = {}
        mock_validate_request_body.return_value = {}
        resp = MagicMock(status_code=200, text='{"id": "1234"}')
        mock_client.return_value = resp

        test_runner = TestRunner("test", "test", version)
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
        assert test_runner.run_tests(job_data, MagicMock()) is None
