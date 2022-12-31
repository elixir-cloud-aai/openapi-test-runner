"""Module unittests.test_cli.py

This module is to test the entry point CLI functionality
"""

import unittest
from unittest.mock import (
    MagicMock,
    mock_open,
    patch
)

from click.testing import CliRunner

from compliance_suite.cli import main, report
from compliance_suite.job_runner import JobRunner
from compliance_suite.report_server import ReportServer


class TestJobRunner(unittest.TestCase):

    def test_main(self):
        """asserts that the 'main' method of cli module can be executed"""

        runner = CliRunner()
        result = runner.invoke(main)
        assert result.exit_code == 0

    @patch.object(JobRunner, "generate_report")
    @patch.object(JobRunner, "run_jobs")
    def test_report_no_tag(self, mock_run_jobs, mock_generate_reports):
        """ asserts if the application is invoked if no tags provided"""

        with patch('builtins.open', mock_open()):
            mock_run_jobs.return_value = {}
            mock_generate_reports.return_value = '{"test": "test"}'
            runner = CliRunner()
            result = runner.invoke(report, [])
            assert result.exit_code == 0

    @patch.object(ReportServer, 'serve_thread')
    @patch.object(JobRunner, "generate_report")
    @patch.object(JobRunner, "run_jobs")
    def test_report(self, mock_run_jobs, mock_generate_reports, mock_report_server):
        """ asserts if the application is invoked if a tag is provided"""

        with patch('builtins.open', mock_open()):
            mock_run_jobs.return_value = {}
            mock_generate_reports.return_value = '{"test": "test"}'
            mock_report_server.return_value = MagicMock()
            runner = CliRunner()
            result = runner.invoke(report, ['--tag', 'All', '--output_path',
                                            "path/to/output", '--serve', '--port', 9090, '--uptime', 1000])
            assert result.exit_code == 0
