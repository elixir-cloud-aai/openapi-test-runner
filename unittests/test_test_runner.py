from test_runner import TestRunner
import json
import os
import unittest
import yaml
from compliance_suite.exceptions.ComplianceException import ComplianceException
from unittest.mock import patch
from requests.models import Response

YAML_SERVICE_INFO_SUCCESS = os.path.join(os.getcwd(), "data", "tests", "success_service_info.yml")
JSON_SERVICE_INFO_SUCCESS = os.path.join(os.getcwd(), "data", "json", "service_info_success.json")
JSON_SERVICE_INFO_FAILURE = os.path.join(os.getcwd(), "data", "json", "service_info_failure.json")
YAML_CREATE_TASK_REQUEST_SUCCESS = os.path.join(os.getcwd(), "data", "tests", "success_create_task.yml")
YAML_CREATE_TASK_REQUEST_FAILURE = os.path.join(os.getcwd(), "data", "tests", "json_error_create_task.yml")


class TestTestRunner(unittest.TestCase):

    def test_validate_logic_success(self):
        with open(YAML_SERVICE_INFO_SUCCESS) as f:
            yaml_data = yaml.safe_load(f)

        test_runner = TestRunner(yaml_data["server"], yaml_data["version"][0])
        test_runner.job_data = yaml_data["jobs"][0]

        with open(JSON_SERVICE_INFO_SUCCESS) as f:
            json_data = json.load(f)
        test_runner.validate_logic(test_runner.job_data["name"], json_data, "Response")
        assert True

    def test_validate_logic_failure(self):
        with open(YAML_SERVICE_INFO_SUCCESS) as f:
            yaml_data = yaml.safe_load(f)

        test_runner = TestRunner(yaml_data["server"], yaml_data["version"][0])
        test_runner.job_data = yaml_data["jobs"][0]

        with open(JSON_SERVICE_INFO_FAILURE) as f:
            json_data = json.load(f)

        with self.assertRaises(ComplianceException):
            test_runner.validate_logic(test_runner.job_data["name"], json_data, "Response")

    def test_validate_request_body_success(self):
        with open(YAML_CREATE_TASK_REQUEST_SUCCESS) as f:
            yaml_data = yaml.safe_load(f)

        test_runner = TestRunner(yaml_data["server"], yaml_data["version"][0])
        test_runner.job_data = yaml_data["jobs"][0]
        test_runner.validate_request_body(yaml_data["jobs"][0]["request_body"])
        assert True

    def test_validate_request_body_failure(self):
        with open(YAML_CREATE_TASK_REQUEST_FAILURE) as f:
            yaml_data = yaml.safe_load(f)

        test_runner = TestRunner(yaml_data["server"], yaml_data["version"][0])
        test_runner.job_data = yaml_data["jobs"][0]
        with self.assertRaises(ComplianceException):
            test_runner.validate_request_body(yaml_data["jobs"][0]["request_body"])

    @patch.object(TestRunner, "validate_logic")
    def test_validate_response_success(self, mock_validate_job):

        mock_validate_job.return_value = {}
        with open(YAML_SERVICE_INFO_SUCCESS) as f:
            yaml_data = yaml.safe_load(f)

        test_runner = TestRunner(yaml_data["server"], yaml_data["version"][0])
        test_runner.job_data = yaml_data["jobs"][0]

        resp = Response()
        resp.status_code = 200
        test_runner.validate_response(resp)
        assert True

    def test_validate_response_failure(self):
        with open(YAML_SERVICE_INFO_SUCCESS) as f:
            yaml_data = yaml.safe_load(f)

        test_runner = TestRunner(yaml_data["server"], yaml_data["version"][0])
        test_runner.job_data = yaml_data["jobs"][0]

        resp = Response()
        resp.status_code = 400
        with self.assertRaises(ComplianceException):
            test_runner.validate_response(resp)