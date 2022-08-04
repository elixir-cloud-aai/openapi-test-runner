from click.testing import CliRunner
from cli import main, report
from job_runner import JobRunner
from unittest.mock import patch
import unittest

class TestJobRunner(unittest.TestCase):

    def test_main(self):
        """asserts that the 'main' method of cli module can be executed"""

        runner = CliRunner()
        runner.invoke(main)
        assert True

    @patch.object(JobRunner, "run_jobs")
    def test_report_no_tag(self, mock_run_jobs):
        mock_run_jobs.return_value = {}
        runner = CliRunner()
        result = runner.invoke(report, [])
        assert result.exit_code == 0
        assert result.output == "Input tag is - ('All',)\n"

    @patch.object(JobRunner, "run_jobs")
    def test_report(self, mock_run_jobs):
        mock_run_jobs.return_value = {}
        runner = CliRunner()
        result = runner.invoke(report, ['--tag', 'All'])
        assert result.exit_code == 0
        assert result.output == "Input tag is - ('All',)\n"
