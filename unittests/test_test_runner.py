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
from compliance_suite.servers.s3 import ServerS3
from compliance_suite.test_runner import TestRunner

YAML_SERVICE_INFO_SUCCESS = os.path.join(os.getcwd(), "unittests", "data", "tests", "success_service_info.yml")
JSON_SERVICE_INFO_SUCCESS = os.path.join(os.getcwd(), "unittests", "data", "json", "service_info_success.json")
JSON_SERVICE_INFO_FAILURE = os.path.join(os.getcwd(), "unittests", "data", "json", "service_info_failure.json")
YAML_CREATE_TASK_REQUEST_SUCCESS = os.path.join(os.getcwd(), "unittests", "data", "tests", "success_create_task.yml")
YAML_CREATE_TASK_REQUEST_FAILURE = os.path.join(os.getcwd(), "unittests", "data", "tests", "json_error_create_task.yml")
YAML_VALIDATE_FUNCTIONAL = os.path.join(os.getcwd(), "unittests", "data", "tests", "validate_functional.yaml")
S3_SERVER_CONFIG_PATH = os.path.join(os.getcwd(),  "unittests", "data", "resources", "s3_server_config.yml")
S3_EMPTY_SERVER_CONFIG_PATH = os.path.join(os.getcwd(), "unittests", "data", "resources", "empty_server_config.yml")


class TestTestRunner(unittest.TestCase):

    @patch('os.path.join')
    def test_validate_logic_success(self, mock_os):
        """ Asserts validate_logic() function for successful schema validation to API Model"""

        mock_os.return_value = S3_SERVER_CONFIG_PATH

        with open(YAML_SERVICE_INFO_SUCCESS) as f:
            yaml_data = yaml.safe_load(f)

        test_runner = TestRunner(yaml_data["service"], yaml_data["server"], yaml_data["version"][0], False)
        test_runner.set_job_data(yaml_data["jobs"][0])

        with open(JSON_SERVICE_INFO_SUCCESS) as f:
            json_data = json.load(f)
        test_runner.validate_logic(test_runner.job_data["name"], json_data, "Response")
        assert True

    @patch('os.path.join')
    def test_validate_logic_failure(self, mock_os):
        """ Asserts validate_logic() function for unsuccessful schema validation to API Model"""

        mock_os.return_value = S3_SERVER_CONFIG_PATH

        with open(YAML_SERVICE_INFO_SUCCESS) as f:
            yaml_data = yaml.safe_load(f)

        test_runner = TestRunner(yaml_data["service"], yaml_data["server"], yaml_data["version"][0], False)
        test_runner.set_job_data(yaml_data["jobs"][0])

        with open(JSON_SERVICE_INFO_FAILURE) as f:
            json_data = json.load(f)

        with self.assertRaises(TestFailureException):
            test_runner.validate_logic(test_runner.job_data["name"], json_data, "Response")

    @patch('os.path.join')
    def test_validate_request_body_success(self, mock_os):
        """ Asserts validate_request_body() function for successful JSON format and schema validation to API Model"""

        mock_os.return_value = S3_SERVER_CONFIG_PATH

        with open(YAML_CREATE_TASK_REQUEST_SUCCESS) as f:
            yaml_data = yaml.safe_load(f)

        test_runner = TestRunner(yaml_data["service"], yaml_data["server"], yaml_data["version"][0], False)
        test_runner.set_job_data(yaml_data["jobs"][0])
        test_runner.validate_request_body(yaml_data["jobs"][0]["request_body"])
        assert True

    @patch.object(ServerS3, 'set_s3_resource')
    @patch.object(ServerS3, 'upload_file')
    @patch('os.path.join')
    def test_validate_request_body_functional_success(self, mock_os, mock_s3_res, mock_upload_file):
        """ Asserts validate_request_body() function for successful JSON format and schema validation to API Model"""

        mock_os.return_value = S3_SERVER_CONFIG_PATH

        mock_s3_res.return_value = MagicMock()
        mock_upload_file.return_value = MagicMock()

        with open(YAML_CREATE_TASK_REQUEST_SUCCESS) as f:
            yaml_data = yaml.safe_load(f)

        test_runner = TestRunner(yaml_data["service"], yaml_data["server"], yaml_data["version"][0], True)
        test_runner.set_job_data(yaml_data["jobs"][0])
        test_runner.validate_request_body(yaml_data["jobs"][0]["request_body"])
        assert True

    @patch('os.path.join')
    def test_validate_request_body_failure(self, mock_os):
        """ Asserts validate_request_body() function for unsuccessful JSON format"""

        mock_os.return_value = S3_SERVER_CONFIG_PATH

        with open(YAML_CREATE_TASK_REQUEST_FAILURE) as f:
            yaml_data = yaml.safe_load(f)

        test_runner = TestRunner(yaml_data["service"], yaml_data["server"], yaml_data["version"][0], False)
        test_runner.set_job_data(yaml_data["jobs"][0])
        with self.assertRaises(JobValidationException):
            test_runner.validate_request_body(yaml_data["jobs"][0]["request_body"])

    @patch.object(ServerS3, 'set_s3_resource')
    @patch.object(ServerS3, 'upload_file')
    @patch('os.path.join')
    def test_validate_request_body_functional_failure(self, mock_os, mock_s3_res, mock_upload_file):
        """ Asserts validate_request_body() function for successful JSON format and schema validation to API Model"""

        mock_os.return_value = S3_EMPTY_SERVER_CONFIG_PATH

        mock_s3_res.return_value = MagicMock()
        mock_upload_file.return_value = MagicMock()

        with open(YAML_CREATE_TASK_REQUEST_SUCCESS) as f:
            yaml_data = yaml.safe_load(f)

        test_runner = TestRunner(yaml_data["service"], yaml_data["server"], yaml_data["version"][0], True)
        test_runner.set_job_data(yaml_data["jobs"][0])
        with self.assertRaises(JobValidationException):
            test_runner.validate_request_body(yaml_data["jobs"][0]["request_body"])

    @patch('os.path.join')
    @patch.object(TestRunner, "validate_logic")
    def test_validate_response_success(self, mock_validate_job, mock_os):
        """ Asserts validate_response() function for successful response and schema validation to API Model"""

        mock_os.return_value = S3_SERVER_CONFIG_PATH
        mock_validate_job.return_value = {}
        with open(YAML_SERVICE_INFO_SUCCESS) as f:
            yaml_data = yaml.safe_load(f)

        test_runner = TestRunner(yaml_data["service"], yaml_data["server"], yaml_data["version"][0], False)
        test_runner.set_job_data(yaml_data["jobs"][0])

        resp = Response()
        resp.status_code = 200
        test_runner.validate_response(resp)
        assert True

    @patch.object(ServerS3, 'delete_bucket_out')
    @patch('os.path.join')
    @patch.object(TestRunner, "validate_logic")
    def test_validate_response_functional_success(self, mock_validate_job, mock_os, mock_delete_bucket):
        """ Asserts validate_response() function for successful response and schema validation to API Model"""

        mock_os.return_value = S3_SERVER_CONFIG_PATH
        mock_validate_job.return_value = {}
        mock_delete_bucket.return_value = None
        with open(YAML_VALIDATE_FUNCTIONAL) as f:
            yaml_data = yaml.safe_load(f)

        test_runner = TestRunner(yaml_data["service"], yaml_data["server"], yaml_data["version"][0], True)
        test_runner.set_job_data(yaml_data["jobs"][0])
        test_runner.set_auxiliary_space("create_task_server", "")

        resp = MagicMock()
        resp.status_code = 200
        resp.json.return_value = {
            "logs": [
                {
                    "logs": [
                        {
                            "stdout": ""
                        }
                    ]
                }
            ]
        }
        test_runner.validate_response(resp)
        assert True

    @patch('os.path.join')
    def test_validate_response_failure(self, mock_os):
        """ Asserts validate_response() function for unsuccessful response"""

        mock_os.return_value = S3_SERVER_CONFIG_PATH

        with open(YAML_SERVICE_INFO_SUCCESS) as f:
            yaml_data = yaml.safe_load(f)

        test_runner = TestRunner(yaml_data["service"], yaml_data["server"], yaml_data["version"][0], False)
        test_runner.set_job_data(yaml_data["jobs"][0])

        resp = Response()
        resp.status_code = 400
        with self.assertRaises(TestFailureException):
            test_runner.validate_response(resp)

    @patch.object(ServerS3, 'delete_bucket_out')
    @patch('os.path.join')
    @patch.object(TestRunner, "validate_logic")
    def test_validate_response_functional_failure(self, mock_validate_job, mock_os, mock_delete_bucket):
        """ Asserts validate_response() function for successful response and schema validation to API Model"""

        mock_os.return_value = S3_SERVER_CONFIG_PATH
        mock_validate_job.return_value = {}
        mock_delete_bucket.return_value = None
        with open(YAML_VALIDATE_FUNCTIONAL) as f:
            yaml_data = yaml.safe_load(f)

        test_runner = TestRunner(yaml_data["service"], yaml_data["server"], yaml_data["version"][0], True)
        test_runner.set_job_data(yaml_data["jobs"][0])
        test_runner.set_auxiliary_space("create_task_server", "")

        resp = MagicMock()
        resp.status_code = 200
        with self.assertRaises(TestFailureException):
            test_runner.validate_response(resp)
