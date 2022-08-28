"""Module unittests.test_cli.py

This module is to test the entry point CLI functionality
"""

import unittest
from unittest.mock import patch

from click.testing import CliRunner

from compliance_suite.cli import main, report
from compliance_suite.job_runner import JobRunner


class TestJobRunner(unittest.TestCase):

    def test_main(self):
        """asserts that the 'main' method of cli module can be executed"""

        runner = CliRunner()
        runner.invoke(main)
        assert True

    @patch.object(JobRunner, "run_jobs")
    def test_report_no_tag(self, mock_run_jobs):
        """ asserts if the application is invoked if no tags provided"""

        mock_run_jobs.return_value = {}
        runner = CliRunner()
        result = runner.invoke(report, [])
        assert result.exit_code == 0

    @patch.object(JobRunner, "run_jobs")
    def test_report(self, mock_run_jobs):
        """ asserts if the application is invoked if a tag is provided"""

        mock_run_jobs.return_value = {}
        runner = CliRunner()
        result = runner.invoke(report, ['--tag', 'All'])
        assert result.exit_code == 0
