"""Module compliance_suite.job_runner.py

This module contains class definition for Job Runner to run the individual YAML Tests from compliance-suite-tests
directory
"""

from pathlib import Path
from typing import (
    Any,
    Dict,
    List
)

from jsonschema import (
    validate,
    ValidationError
)
import yaml

from compliance_suite.constants.constants import (
    PATTERN_HASH_CENTERED,
    PATTERN_HASH_SPACED
)
from compliance_suite.exceptions.compliance_exception import (
    JobValidationException,
    TestFailureException,
    TestRunnerException
)
from compliance_suite.functions.log import logger
from compliance_suite.functions.report import (
    Report,
    ReportUtility
)
from compliance_suite.test_runner import TestRunner
from compliance_suite.utils.test_utils import tag_matcher
from ga4gh.testbed.report.test import Test


class JobRunner:
    """Class to run the individual YAML Tests"""

    def __init__(self, server: str, version: str):
        """Initialize the Job Runner object

        Args:
            server (str): The server URL on which the compliance suite will be run
            version (str): The compliance suite will be run against this TES version
        """

        self.server: str = server
        self.version: str = version
        self.include_tags: List[str] = []
        self.exclude_tags: List[str] = []
        self.test_path: List[str] = []
        self.test_count: int = 0
        self.test_status: Dict = {        # To store the status of each test
            "passed": [],
            "failed": [],
            "skipped": []
        }
        self.report = Report()

    def set_report(self, report: Any) -> None:
        """Set the report data member

        Args:
            report (Any): The report object to be defined for use inside the class
        """
        self.report = report

    def set_tags(self, include_tags: List[str], exclude_tags: List[str]) -> None:
        """ Set the tags to determine which tests will be run

        Args:
            include_tags: User-provided list of tags for which the compliance suite will be run
            exclude_tags: User-provided list of tags for which the compliance suite will not be run
        """

        self.include_tags = include_tags
        self.exclude_tags = exclude_tags

    def set_test_path(self, input_test_path: List[str]) -> None:
        """ Set the test path

        Args:
            input_test_path: The relative path of the test file/directory from project root
        """

        self.test_path = input_test_path

    def generate_summary(self) -> None:
        """Generate test summary at the completion"""

        passed_tests: str = ", ".join(self.test_status["passed"])
        failed_tests: str = ", ".join(self.test_status["failed"])
        skipped_tests: str = ", ".join(self.test_status["skipped"])
        passed_tests_count: int = len(self.test_status["passed"])
        failed_tests_count: int = len(self.test_status["failed"])
        skipped_tests_count: int = len(self.test_status["skipped"])

        logger.summary("\n\n\n")
        logger.summary("   Compliance Testing Summary   ", PATTERN_HASH_CENTERED)
        logger.summary("", PATTERN_HASH_SPACED)
        logger.summary(f"Total Tests - {self.test_count}", PATTERN_HASH_SPACED)
        logger.summary(f'Passed - {passed_tests_count} ({passed_tests})', PATTERN_HASH_SPACED)
        logger.summary(f'Failed - {failed_tests_count} ({failed_tests})', PATTERN_HASH_SPACED)
        logger.summary(f'Skipped - {skipped_tests_count} ({skipped_tests})', PATTERN_HASH_SPACED)
        logger.summary("", PATTERN_HASH_SPACED)
        logger.summary("", PATTERN_HASH_CENTERED)
        logger.summary("\n\n\n")

    def validate_job(
            self,
            yaml_data: Any,
            yaml_file: str
    ) -> None:
        """ Validates if the Test file is in conformance to the test template/schema

        Args:
            yaml_data (Any): The parsed yaml data to perform the schema checks
            yaml_file (str): The yaml file name
        """

        schema_path = Path("docs/template/test_template_schema.json")
        with open(str(schema_path), "r") as f:
            json_schema: Any = yaml.safe_load(f)

        try:
            validate(yaml_data, json_schema)
            logger.info(f'Test YAML file valid for {yaml_file}')
        except ValidationError as err:
            raise JobValidationException(name="YAML Schema Validation Error",
                                         message=f"YAML file {yaml_file} does not match the Test template/schema",
                                         details=err.message)

    def generate_report(self) -> Any:
        """Generates the report via ga4gh-testbed-lib and returns it

        Return:
            (Any): Returns the JSON compliance report
        """

        json_report = self.report.generate()
        return json_report

    def initialize_test(self, yaml_file: Path) -> None:
        """ Initializes a test based on the provided YAML file.

        Args:
            yaml_file: The path to the YAML file containing the test data.
        """

        self.test_count += 1
        report_job_test = Test()
        logger.summary("\n")
        logger.summary(f"     Initiating Test-{self.test_count} for {yaml_file}     ", PATTERN_HASH_CENTERED)

        try:
            with open(str(yaml_file), "r") as f:
                try:
                    yaml_data: Any = yaml.safe_load(f)
                except yaml.YAMLError as err:
                    raise JobValidationException(name="YAML Error",
                                                 message=f"Invalid YAML file {yaml_file}",
                                                 details=err)
            self.validate_job(yaml_data, str(yaml_file))
            report_phase = self.report.add_phase(str(yaml_file), yaml_data["description"])

            if (self.version in yaml_data["versions"]
                    and tag_matcher(self.include_tags, self.exclude_tags, yaml_data["tags"])):
                test_runner = TestRunner(yaml_data["service"], self.server, self.version)
                job_count: int = 0
                for job in yaml_data["jobs"]:
                    job_count += 1
                    logger.info(f'Running tests for sub-job-{job_count} -> {job["name"]}')
                    report_job_test = report_phase.add_test()
                    test_runner.run_tests(job, report_job_test)
                self.test_status["passed"].append(str(self.test_count))
                logger.success(f'Compliance Test-{self.test_count} for {yaml_file} successful.')
            else:
                self.test_status["skipped"].append(str(self.test_count))
                logger.skip(f"Version or tag did not match. Skipping Test-{self.test_count} for {yaml_file}")
        except (JobValidationException, TestFailureException) as err:
            self.test_status["failed"].append(str(self.test_count))
            logger.error(f'Compliance Test-{self.test_count} for {yaml_file} failed.')
            logger.error(err)
        except TestRunnerException as err:
            self.test_status["failed"].append(str(self.test_count))
            logger.error(f'Compliance Test-{self.test_count} for {yaml_file} failed.')
            logger.error(err)
            report_custom_case = report_job_test.add_case()
            ReportUtility.set_case(case=report_custom_case,
                                   name="test_runner_exception",
                                   description="Runtime exception thrown in Compliance Suite")
            ReportUtility.case_fail(case=report_custom_case,
                                    message=f'{err.name}. {err.message}',
                                    log_message=str(err.details))

    def run_jobs(self) -> None:
        """ Reads the Test files from compliance-suite-tests directory. Validates and parses individual jobs.
        The individual jobs are then executed via Test Runner"""

        report = Report()
        self.set_report(report)
        self.report.set_platform_details(self.server)

        for test_path in self.test_path:
            search_path = Path(test_path)
            if search_path.is_file() and search_path.match("*.yml"):
                self.initialize_test(search_path)
            elif search_path.is_dir():
                for yaml_file in search_path.glob("**/*.yml"):
                    self.initialize_test(yaml_file)

        self.generate_summary()
