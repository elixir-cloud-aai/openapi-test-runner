"""Module unittests.test_cli.py

This module is to test the entry point CLI functionality
"""

from unittest.mock import (
    MagicMock,
    mock_open,
    patch
)

from click.testing import CliRunner
import pytest

from compliance_suite.cli import main, report
from compliance_suite.job_runner import JobRunner
from compliance_suite.report_server import ReportServer
from unittests.data.constants import (
    TEST_URL,
    TEST_VERSIONS
)


class TestJobRunner:

    def test_main(self):
        """asserts that the 'main' method of cli module can be executed"""

        runner = CliRunner()
        result = runner.invoke(main)
        assert result.exit_code == 0

    def test_report_no_server(self):
        """ asserts if the application raises Exception if no server is provided"""

        runner = CliRunner()
        result = runner.invoke(report, [])
        assert result.exit_code == 1

    def test_report_no_version(self):
        """ asserts if the application raises Exception if no server is provided"""

        runner = CliRunner()
        result = runner.invoke(report, ['--server', TEST_URL])
        assert result.exit_code == 1

    @pytest.mark.parametrize("version", TEST_VERSIONS)
    @patch.object(JobRunner, "generate_report")
    @patch.object(JobRunner, "run_jobs")
    def test_report_no_tag(self, mock_run_jobs, mock_generate_reports, version):
        """ asserts if the application is invoked if no tags provided"""

        with patch('builtins.open', mock_open()):
            mock_run_jobs.return_value = {}
            mock_generate_reports.return_value = '{"test": "test"}'
            runner = CliRunner()
            result = runner.invoke(report, ['--server', TEST_URL, '--version', version])
            assert result.exit_code == 0

    @pytest.mark.parametrize("version", TEST_VERSIONS)
    @patch.object(ReportServer, 'serve_thread')
    @patch.object(JobRunner, "generate_report")
    @patch.object(JobRunner, "run_jobs")
    def test_report(self, mock_run_jobs, mock_generate_reports, mock_report_server, version):
        """ asserts if the application is invoked if a tag is provided"""

        with patch('builtins.open', mock_open()):
            mock_run_jobs.return_value = {}
            mock_generate_reports.return_value = '{"test": "test"}'
            mock_report_server.return_value = MagicMock()
            runner = CliRunner()
            result = runner.invoke(report, ['--server', TEST_URL, '--version', version, '--tag', 'All',
                                            '--output_path', "path/to/output", '--serve', '--port', 9090,
                                            '--uptime', 1000])
            assert result.exit_code == 0

    @pytest.mark.parametrize("version", TEST_VERSIONS)
    @patch.object(JobRunner, "get_test_status")
    @patch.object(JobRunner, "generate_report")
    @patch.object(JobRunner, "run_jobs")
    def test_report_failed_tests(self, mock_run_jobs, mock_generate_reports, mock_test_status, version):
        """ asserts if the application exits with error code 1 if any tests fail """

        with patch('builtins.open', mock_open()):
            mock_run_jobs.return_value = {}
            mock_generate_reports.return_value = '{"test": "test"}'
            mock_test_status.return_value = {"failed": [str(1)]}
            runner = CliRunner()
            result = runner.invoke(report, ['--server', TEST_URL, '--version', version])
            assert result.exit_code == 1
