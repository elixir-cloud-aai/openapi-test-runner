"""Module unittests.test_job_runner.py

This module is to test the Job Runner class and its methods
"""

from pathlib import Path
from unittest.mock import (
    MagicMock,
    patch
)

import pytest

from compliance_suite.exceptions.compliance_exception import (
    JobValidationException,
    TestRunnerException
)
from compliance_suite.functions.report import Report
from compliance_suite.job_runner import JobRunner
from compliance_suite.test_runner import TestRunner
from unittests.data.constants import TEST_URL


YAML_TEMPLATE_PATH_SUCCESS = Path("unittests/data/templates/success_template.yml")
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

    def test_load_and_validate_yaml_data_test(self):
        """ Asserts validate job functions for proper YAML schema"""

        job_runner_object = JobRunner(TEST_URL, "1.0.0")
        yaml_data = job_runner_object.load_and_validate_yaml_data(str(YAML_TEST_PATH_SUCCESS), "Test")
        assert "service" in yaml_data

    def test_load_and_validate_yaml_data_template(self):
        """ Asserts validate job functions for proper YAML schema"""

        job_runner_object = JobRunner(TEST_URL, "1.0.0")
        yaml_data = job_runner_object.load_and_validate_yaml_data(str(YAML_TEMPLATE_PATH_SUCCESS), "Template")
        assert "endpoint" in yaml_data[0]

    def test_load_and_validate_yaml_data_failure(self):
        """ Asserts validate_job() function for incorrect YAML schema"""

        with pytest.raises(JobValidationException):
            job_runner_object = JobRunner(TEST_URL, "1.0.0")
            job_runner_object.load_and_validate_yaml_data(str(YAML_WRONG_SCHEMA), "Test")

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

    @patch.object(TestRunner, 'run_tests')
    def test_initialize_test(self, mock_run_tests):
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
