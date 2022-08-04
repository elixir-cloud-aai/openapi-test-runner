import job_runner
from compliance_suite.exceptions.ComplianceException import ComplianceException
from job_runner import JobRunner
import unittest
from unittest.mock import patch
import yaml
import os

SCHEMA_PATH = os.path.join(os.getcwd(), "tests", "template", "test_template_schema.json")
YAML_TEST_PATH = os.path.join(os.getcwd(), "unittests", "data", "run_job_tests")
YAML_TEST_PATH_SUCCESS = os.path.join(os.getcwd(), "unittests", "data", "run_job_tests", "success_01.yml")
YAML_TEST_PATH_INVALID = os.path.join(os.getcwd(), "unittests", "data", "run_job_tests", "invalid_yaml.yml")
YAML_TEST_PATH_SKIP = os.path.join(os.getcwd(), "unittests", "data", "run_job_tests", "skip_01.yml")
YAML_SERVICE_INFO_SUCCESS = os.path.join(os.getcwd(), "unittests", "data", "tests", "success_service_info.yml")
YAML_WRONG_SCHEMA = os.path.join(os.getcwd(), "unittests", "data", "tests", "wrong_schema_yaml.yml")
YAML_INVALID = os.path.join(os.getcwd(), "unittests", "data", "tests", "invalid_yaml.yml")


class TestJobRunner(unittest.TestCase):

    def test_generate_summary(self):
        job_runner_object = JobRunner("")
        job_runner_object.generate_summary()
        assert True

    @patch("os.path.join", return_value=SCHEMA_PATH)
    def test_validate_job_success(self, mock_os):
        with open(YAML_SERVICE_INFO_SUCCESS, "r") as f:
            yaml_data = yaml.safe_load(f)

        job_runner_object = JobRunner("")
        job_runner_object.validate_job(yaml_data, "success_service_info.yml")
        assert True

    @patch('os.path.join', return_value=SCHEMA_PATH)
    def test_validate_job_failure(self, mock_os):
        with open(YAML_WRONG_SCHEMA, "r") as f:
            yaml_data = yaml.safe_load(f)

        with self.assertRaises(ComplianceException):
            job_runner_object = JobRunner("")
            job_runner_object.validate_job(yaml_data, "wrong_schema_yaml.yml")

    def test_validate_yaml_success(self):
        with open(YAML_SERVICE_INFO_SUCCESS, "r") as f:
            job_runner_object = JobRunner("")
            job_runner_object.validate_yaml(f, "success_service_info.yml")
            assert True

    def test_validate_yaml_failure(self):
        with open(YAML_INVALID, "r") as f:
            with self.assertRaises(ComplianceException):
                job_runner_object = JobRunner("")
                job_runner_object.validate_yaml(f, "invalid_yaml.yml")

    @patch('os.path.join')
    def test_run_jobs_success(self, mock_os):
        mock_os.side_effect = [YAML_TEST_PATH, YAML_TEST_PATH_INVALID, YAML_TEST_PATH_SKIP, SCHEMA_PATH,
                               YAML_TEST_PATH_SUCCESS, SCHEMA_PATH]
        tag = "All",
        job_runner_object = JobRunner(tag)
        job_runner_object.run_jobs()
        assert True
