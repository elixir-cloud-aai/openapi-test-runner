"""Module unittests.test_job_runner.py

This module is to test the Job Runner class and its methods
"""

import os
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
from compliance_suite.job_runner import JobRunner
from compliance_suite.test_runner import TestRunner
from unittests.data.constants import (
    TEST_URL,
    TEST_VERSIONS
)


SCHEMA_PATH = os.path.join(os.getcwd(), "tests", "template", "test_template_schema.json")
YAML_TEST_PATH = os.path.join(os.getcwd(), "unittests", "data", "run_job_tests")
YAML_TEST_PATH_SUCCESS = os.path.join(os.getcwd(), "unittests", "data", "run_job_tests", "success_01.yml")
YAML_TEST_PATH_INVALID = os.path.join(os.getcwd(), "unittests", "data", "run_job_tests", "invalid_yaml.yml")
YAML_TEST_PATH_SKIP = os.path.join(os.getcwd(), "unittests", "data", "run_job_tests", "skip_01.yml")
YAML_TEST_PATH_FAIL = os.path.join(os.getcwd(), "unittests", "data", "run_job_tests", "fail_service_info.yml")
YAML_WRONG_SCHEMA = os.path.join(os.getcwd(), "unittests", "data", "tests", "wrong_schema_yaml.yml")


class TestJobRunner:

    @pytest.mark.parametrize("version", TEST_VERSIONS)
    def test_generate_summary(self, version):
        """ Checks if generate summary functions runs successfully"""

        job_runner_object = JobRunner(TEST_URL, version, [], [])
        assert job_runner_object.generate_summary() is None

    @pytest.mark.parametrize("version", TEST_VERSIONS)
    def test_generate_report(self, version):
        """ Checks if generate summary functions runs successfully"""

        job_runner_object = JobRunner(TEST_URL, version, [], [])
        job_runner_object.set_report(MagicMock())
        job_runner_object.generate_report()
        assert True

    @pytest.mark.parametrize("version", TEST_VERSIONS)
    def test_tag_matcher_success(self, version):
        job_runner_object = JobRunner(TEST_URL, version, ["tag"], [])
        assert job_runner_object.tag_matcher(["tag", "tag1", "tag2"]) is True

    @pytest.mark.parametrize("version", TEST_VERSIONS)
    def test_tag_matcher_fail(self, version):
        job_runner_object = JobRunner(TEST_URL, version, [], ["tag"])
        assert job_runner_object.tag_matcher(["tag", "tag1", "tag2"]) is False

    @pytest.mark.parametrize("version", TEST_VERSIONS)
    def test_version_matcher_success(self, version):
        job_runner_object = JobRunner(TEST_URL, version, ["tag"], [])
        assert job_runner_object.version_matcher(TEST_VERSIONS) is True

    def test_version_matcher_fail(self):
        job_runner_object = JobRunner(TEST_URL, '0.0.0', ["tag"], [])
        assert job_runner_object.version_matcher(TEST_VERSIONS) is False

    @pytest.mark.parametrize("version", TEST_VERSIONS)
    @patch("os.path.join", return_value=SCHEMA_PATH)
    def test_validate_job_success(self, mock_os, version):
        """ Asserts validate job functions for proper YAML schema"""

        with open(YAML_TEST_PATH_SUCCESS, "r") as f:
            yaml_data = yaml.safe_load(f)

        job_runner_object = JobRunner(TEST_URL, version, [], [])
        assert job_runner_object.validate_job(yaml_data, "success_01.yml") is None

    @pytest.mark.parametrize("version", TEST_VERSIONS)
    @patch('os.path.join', return_value=SCHEMA_PATH)
    def test_validate_job_failure(self, mock_os, version):
        """ Asserts validate_job() function for incorrect YAML schema"""

        with open(YAML_WRONG_SCHEMA, "r") as f:
            yaml_data = yaml.safe_load(f)

        with pytest.raises(JobValidationException):
            job_runner_object = JobRunner(TEST_URL, version, [], [])
            job_runner_object.validate_job(yaml_data, "wrong_schema_yaml.yml")

    @pytest.mark.parametrize("version", TEST_VERSIONS)
    @patch.object(JobRunner, 'validate_job')
    @patch.object(TestRunner, 'run_tests')
    @patch('os.path.join')
    def test_run_jobs_success(self, mock_os, mock_run_tests, mock_validate_job, version):
        """ Asserts run_jobs() for unit test YAML files"""

        mock_run_tests.side_effect = [TestRunnerException(name="test", message="test", details="test"), None, None]
        mock_validate_job.return_value = {}

        mock_os.side_effect = [YAML_TEST_PATH, YAML_TEST_PATH_FAIL, YAML_TEST_PATH_INVALID, YAML_TEST_PATH_SKIP,
                               YAML_TEST_PATH_SUCCESS]
        include_tags = ["all"]
        job_runner_object = JobRunner(TEST_URL, version, include_tags, [])
        assert job_runner_object.run_jobs() is None
