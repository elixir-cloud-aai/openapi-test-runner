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
from unittests.data.constants import (
    TEST_SERVICE,
    TEST_URL,
    TEST_VERSIONS
)


class TestTestRunner:

    @pytest.fixture
    def default_test_runner(self):
        """Pytest fixture for default test runner with required job fields"""

        test_runner = TestRunner(TEST_SERVICE, TEST_URL, "x.y.z")
        test_runner.report_test = MagicMock()
        test_runner.job_data = {
            "name": "test",
            "operation": "test",
            "endpoint": "test",
            "response": {"200": ""}
        }
        return test_runner

    @pytest.mark.parametrize("version", TEST_VERSIONS)      # Use parameterized versions once to cover all models
    def test_validate_logic_success(self, version):
        """ Asserts validate_logic() function for successful schema validation to API Model"""

        test_runner = TestRunner(TEST_SERVICE, TEST_URL, version)
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

    def test_validate_logic_failure(self):
        """ Asserts validate_logic() function for unsuccessful schema validation to API Model"""

        test_runner = TestRunner(TEST_SERVICE, TEST_URL, "1.0.0")
        test_runner.set_job_data(
            {
                "operation": "test",
                "endpoint": "test"
            }
        )
        test_runner.report_test = MagicMock()
        with pytest.raises(TestFailureException):
            test_runner.validate_logic("service_info", {}, "Response")

    @patch.object(TestRunner, "validate_logic")
    def test_validate_request_body_success(self, mock_validate_job):
        """ Asserts validate_request_body() function for successful JSON format and schema validation to API Model"""

        mock_validate_job.return_value = {}

        test_runner = TestRunner(TEST_SERVICE, TEST_URL, "1.0.0")
        test_runner.set_job_data(
            {
                "name": "test",
                "operation": "test",
                "endpoint": "test"
            }
        )
        test_runner.report_test = MagicMock()
        assert test_runner.validate_request_body("{}") is None

    def test_validate_request_body_failure(self):
        """ Asserts validate_request_body() function for unsuccessful JSON format"""

        test_runner = TestRunner(TEST_SERVICE, TEST_URL, "1.0.0")
        test_runner.set_job_data(
            {
                "operation": "test",
                "endpoint": "test"
            }
        )
        test_runner.report_test = MagicMock()
        with pytest.raises(JobValidationException):
            test_runner.validate_request_body("{")

    @patch.object(TestRunner, "validate_logic")
    def test_validate_response_success_get(self, mock_validate_job):
        """ Asserts validate_response() function for successful response and schema validation to API Model"""

        mock_validate_job.return_value = {}

        test_runner = TestRunner(TEST_SERVICE, TEST_URL, "1.0.0")
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

    @patch.object(TestRunner, "validate_logic")
    def test_validate_response_success(self, mock_validate_job):
        """ Asserts validate_response() function for successful response and schema validation to API Model"""

        mock_validate_job.return_value = {}

        test_runner = TestRunner(TEST_SERVICE, TEST_URL, "1.0.0")
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

    def test_validate_response_failure(self):
        """ Asserts validate_response() function for unsuccessful response"""

        test_runner = TestRunner(TEST_SERVICE, TEST_URL, "1.0.0")
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

    @patch.object(Client, "poll_request")
    @patch.object(TestRunner, "validate_response")
    def test_run_jobs_get_task(self, mock_validate_response, mock_client):
        """Assert the run job method for get task to be successful"""

        mock_validate_response.return_value = {}
        mock_client.return_value = MagicMock()

        test_runner = TestRunner(TEST_SERVICE, TEST_URL, "1.0.0")
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

    @patch.object(Client, "send_request")
    @patch.object(TestRunner, "validate_request_body")
    @patch.object(TestRunner, "validate_logic")
    def test_run_jobs_create_task(self, mock_validate_logic, mock_validate_request_body, mock_client):
        """Assert the run job method for create task to be successful"""

        mock_validate_logic.return_value = {}
        mock_validate_request_body.return_value = {}
        resp = MagicMock(status_code=200, text='{"id": "1234"}')
        mock_client.return_value = resp

        test_runner = TestRunner(TEST_SERVICE, TEST_URL, "1.0.0")
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

    def test_validate_filters_string_success(self, default_test_runner):
        """Assert validate filters to be successful for string type"""

        default_test_runner.job_data["filter"] = [
            {
                "path": "$response.root",
                "type": "string",
                "value": "hello world",
                "size": 11
            },
            {
                "path": "$response.name",
                "type": "string",
                "regex": "true",
                "value": "^pre"
            }
        ]
        json_data = {
            "root": "hello world",
            "name": "prefix"
        }
        assert default_test_runner.validate_filters(json_data) is None

    def test_validate_filters_string_failure(self, default_test_runner):
        """Assert validate filters to fail for string type"""

        default_test_runner.job_data["filter"] = [{
            "path": "$response.root",
            "type": "string",
            "value": "hello world",
            "size": 100
        }]
        json_data = {
            "root": "hello world",
            "name": "prefix"
        }
        with pytest.raises(TestFailureException):
            default_test_runner.validate_filters(json_data)

    def test_validate_filters_array_success(self, default_test_runner):
        """Assert validate filters to be successful for array type"""

        default_test_runner.job_data["filter"] = [{
            "path": "$response.root",
            "type": "array",
            "value": "hello",
            "size": 4
        }]
        json_data = {
            "root": ["hello", "world", "lorem", "ipsum"]
        }
        assert default_test_runner.validate_filters(json_data) is None

    def test_validate_filters_array_failure(self, default_test_runner):
        """Assert validate filters to fail for array type"""

        default_test_runner.job_data["filter"] = [{
            "path": "$response.root",
            "type": "array",
            "value": "hello",
            "size": 100
        }]
        json_data = {
            "root": ["hello", "world", "lorem", "ipsum"]
        }
        with pytest.raises(TestFailureException):
            default_test_runner.validate_filters(json_data)

    def test_validate_filters_object_success(self, default_test_runner):
        """Assert validate filters to be successful for object type"""

        default_test_runner.job_data["filter"] = [{
            "path": "$response.root",
            "type": "object",
            "value": '{"foo": "bar", "hello": "world"}',
            "size": 3
        }]
        json_data = {
            "root": {
                "hello": "world",
                "lorem": "ipsum",
                "foo": "bar"
            }
        }
        assert default_test_runner.validate_filters(json_data) is None

    def test_validate_filters_object_failure(self, default_test_runner):
        """Assert validate filters to fail for object type"""

        default_test_runner.job_data["filter"] = [{
            "path": "$response.root",
            "type": "object",
            "value": '{"foo": "bar", "hello": "world"}',
            "size": 100
        }]
        json_data = {
            "root": {
                "hello": "world",
                "lorem": "ipsum",
                "foo": "bar"
            }
        }
        with pytest.raises(TestFailureException):
            default_test_runner.validate_filters(json_data)

    def test_validate_filters_type_failure(self, default_test_runner):
        """Assert validate filters to fail for invalid type"""

        default_test_runner.job_data["filter"] = [{
            "path": "$response.root",
            "type": "array",
            "value": "hello world",
        }]
        json_data = {
            "root": "hello world"
        }
        with pytest.raises(JobValidationException):
            default_test_runner.validate_filters(json_data)

    def test_transform_path_parameters_success(self, default_test_runner):
        """Assert transform_path_parameters to be successful"""

        default_test_runner.set_auxiliary_space("storage_key", "value")
        path_params = {
            "path_key": "{storage_key}"
        }
        transformed_path_params = default_test_runner.transform_parameters(path_params)
        assert transformed_path_params["path_key"] == "value"

    def test_transform_path_parameters_failure(self, default_test_runner):
        """Assert transform_path_parameters to fail due to invalid storage variable"""

        default_test_runner.set_auxiliary_space("wrong_storage_key", "value")
        default_test_runner.job_data["description"] = "Description"
        default_test_runner.job_data["path_parameters"] = {
            "path_key": "{storage_key}"
        }

        with pytest.raises(JobValidationException):
            default_test_runner.run_tests(default_test_runner.job_data, default_test_runner.report_test)
