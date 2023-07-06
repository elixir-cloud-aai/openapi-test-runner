"""Module unittests.test_cli.py

This module is to test the entry point CLI functionality
"""

from unittest.mock import (
    MagicMock,
    mock_open,
    patch
)

from click.testing import CliRunner

from compliance_suite.cli import main, report
from compliance_suite.job_runner import JobRunner
from compliance_suite.report_server import ReportServer
from unittests.data.constants import TEST_URL


class TestJobRunner:

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
            result = runner.invoke(report, ['--server', TEST_URL, '--version', '1.0.0'])
            assert result.exit_code == 0

    @patch.object(ReportServer, 'serve_thread')
    @patch.object(JobRunner, "generate_report")
    @patch.object(JobRunner, "run_jobs")
    def test_report(self, mock_run_jobs, mock_generate_reports, mock_report_server):
        """ asserts if the application is invoked if the report output path is provided"""

        with patch('builtins.open', mock_open()):
            mock_run_jobs.return_value = {}
            mock_generate_reports.return_value = '{"test": "test"}'
            mock_report_server.return_value = MagicMock()
            runner = CliRunner()
            result = runner.invoke(report, ['--server', TEST_URL, '--version', '1.0.0', '--include-tags', 'test',
                                            '--output_path', "path/to/output", '--serve', '--port', 9090,
                                            '--uptime', 1000])
            assert result.exit_code == 0

    def test_validate_regex_failure(self):
        """Asserts if the application raises CLI error if invalid regex is provided for tags"""

        runner = CliRunner()
        result = runner.invoke(report, ['--server', TEST_URL, '--version', '1.0.0', '--exclude-tags', '%%INVALID%%'])
        assert result.exit_code == 2
        assert "Only letters (a-z, A-Z), digits (0-9) and underscores (_) are allowed." in result.output

    def test_invalid_test_path(self):
        """Assert the application throws an exception if invalid test path is provided"""

        runner = CliRunner()
        result = runner.invoke(report, ['--server', TEST_URL, '--version', '1.0.0', '--test-path', 'invalid/path'])

        assert result.exit_code == 1
        assert result.exception.__class__ == FileNotFoundError
        assert "Test path: invalid/path not found" in result.exception.__str__()
