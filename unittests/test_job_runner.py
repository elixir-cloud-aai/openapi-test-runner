"""Module unittests.test_job_runner.py

This module is to test the Job Runner class and its methods
"""

from pathlib import Path
from unittest.mock import (
    MagicMock,
    patch
)

import pytest
import yaml

from compliance_suite.exceptions.compliance_exception import (
    JobValidationException,
    TestRunnerException
)
from compliance_suite.functions.report import Report
from compliance_suite.job_runner import JobRunner
from compliance_suite.test_runner import TestRunner
from unittests.data.constants import TEST_URL


YAML_TEST_PATH_SUCCESS = Path("unittests/data/run_job_tests/success_01.yml")
YAML_TEST_PATH_INVALID = Path("unittests/data/run_job_tests/invalid_yaml.yml")
YAML_TEST_PATH_SKIP = Path("unittests/data/run_job_tests/skip_01.yml")
YAML_TEST_PATH_FAIL = Path("unittests/data/run_job_tests/fail_service_info.yml")
YAML_WRONG_SCHEMA = Path("unittests/data/tests/wrong_schema_yaml.yml")


class TestJobRunner:

    def test_generate_summary(self):
        """ Checks if generate summary functions runs successfully"""

        job_runner_object = JobRunner(TEST_URL, "1.0.0")
        assert job_runner_object.generate_summary() is None

    def test_generate_report(self):
        """ Checks if generate summary functions runs successfully"""

        job_runner_object = JobRunner(TEST_URL, "1.0.0")
        job_runner_object.set_report(MagicMock())
        job_runner_object.generate_report()
        assert True

    def test_validate_job_success(self):
        """ Asserts validate job functions for proper YAML schema"""

        with open(YAML_TEST_PATH_SUCCESS, "r") as f:
            yaml_data = yaml.safe_load(f)

        job_runner_object = JobRunner(TEST_URL, "1.0.0")
        assert job_runner_object.validate_job(yaml_data, "success_01.yml") is None

    def test_validate_job_failure(self):
        """ Asserts validate_job() function for incorrect YAML schema"""

        with open(YAML_WRONG_SCHEMA, "r") as f:
            yaml_data = yaml.safe_load(f)

        with pytest.raises(JobValidationException):
            job_runner_object = JobRunner(TEST_URL, "1.0.0")
            job_runner_object.validate_job(yaml_data, "wrong_schema_yaml.yml")

    @patch.object(JobRunner, 'initialize_test')
    def test_run_jobs_file(self, mock_initialize_test):
        job_runner_object = JobRunner(TEST_URL, "1.0.0")
        job_runner_object.set_test_path(["unittests/data/run_job_tests/success_01.yml"])
        job_runner_object.run_jobs()
        mock_initialize_test.assert_called_once()

    @patch.object(JobRunner, 'initialize_test')
    def test_run_jobs_dir(self, mock_initialize_test):
        job_runner_object = JobRunner(TEST_URL, "1.0.0")
        job_runner_object.set_test_path(["unittests/data/run_job_tests"])
        job_runner_object.run_jobs()
        assert mock_initialize_test.call_count == len(list(Path("unittests/data/run_job_tests").glob("**/*.yml")))

    @patch.object(JobRunner, 'validate_job')
    @patch.object(TestRunner, 'run_tests')
    def test_initialize_test(self, mock_run_tests, mock_validate_job):
        job_runner_object = JobRunner(TEST_URL, "1.0.0")
        job_runner_object.set_report(Report())

        job_runner_object.initialize_test(YAML_TEST_PATH_SUCCESS)
        assert len(job_runner_object.test_status["passed"]) == 1

        job_runner_object.initialize_test(YAML_TEST_PATH_SKIP)
        assert len(job_runner_object.test_status["skipped"]) == 1

        mock_run_tests.side_effect = [TestRunnerException("test", "test", "test")]
        job_runner_object.initialize_test(YAML_TEST_PATH_FAIL)
        assert len(job_runner_object.test_status["failed"]) == 1

    @patch.object(TestRunner, 'run_tests')
    def test_initialize_test_invalid_job(self, mock_run_tests):
        job_runner_object = JobRunner(TEST_URL, "1.0.0")
        job_runner_object.set_report(MagicMock())
        job_runner_object.initialize_test(YAML_TEST_PATH_INVALID)
        assert len(job_runner_object.test_status["failed"]) == 1
