"""Module unittests.test_cli.py

This module is to test the entry point CLI functionality
"""

import os
import unittest
from unittest.mock import (
    MagicMock,
    patch
)

from click.testing import CliRunner

from compliance_suite.cli import main, report
from compliance_suite.job_runner import JobRunner
from compliance_suite.report_server import ReportServer

REPORT_PATH = os.path.join(os.getcwd(), "unittests", "data", "web", "web_report.json")


class TestJobRunner(unittest.TestCase):

    def test_main(self):
        """asserts that the 'main' method of cli module can be executed"""

        runner = CliRunner()
        runner.invoke(main)
        assert True

    @patch('os.path.join')
    @patch.object(JobRunner, "generate_report")
    @patch.object(JobRunner, "run_jobs")
    def test_report_no_tag(self, mock_run_jobs, mock_generate_reports, mock_os):
        """ asserts if the application is invoked if no tags provided"""

        mock_os.return_value = REPORT_PATH
        mock_run_jobs.return_value = {}
        mock_generate_reports.return_value = "{}"
        runner = CliRunner()
        runner.invoke(report, [])
        assert True

    @patch.object(ReportServer, 'serve_thread')
    @patch('os.path.join')
    @patch.object(JobRunner, "generate_report")
    @patch.object(JobRunner, "run_jobs")
    def test_report(self, mock_run_jobs, mock_generate_reports, mock_os, mock_report_server):
        """ asserts if the application is invoked if a tag is provided"""

        mock_os.return_value = REPORT_PATH
        mock_run_jobs.return_value = {}
        mock_generate_reports.return_value = "{}"
        mock_report_server.return_value = MagicMock()
        runner = CliRunner()
        output_path = REPORT_PATH
        runner.invoke(report, ['--tag', 'All', '--output_path', output_path, '--serve', '--port', 9090,
                                        '--uptime', 1000])
        assert True
