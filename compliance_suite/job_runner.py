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
    RefResolver,
    validate,
    ValidationError
)
import yaml

from compliance_suite.constants.constants import (
    PATTERN_HASH_CENTERED,
    PATTERN_HASH_SPACED,
    TEMPLATE,
    TEST
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
from compliance_suite.utils.test_utils import (
    replace_string,
    tag_matcher
)
from ga4gh.testbed.report.test import Test


class JobRunner:
    """Class to run the individual YAML Tests"""

    def __init__(self, server: str, version: str):
        """Initialize the Job Runner object

        Args:
            server (str): The server URL on which the compliance suite will be run
            version (str): The compliance suite will be run against this API version
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

    def load_and_validate_yaml_data(self, yaml_file: str, _type: str) -> Any:
        """
        Load and validate YAML data from the file with the provided schema type.

        Args:
            yaml_file: The path to the YAML file.
            _type: The type of YAML file, either "Test" or "Template".

        Returns:
            The loaded and validated YAML data.
        """

        # Load YAML data
        try:
            # yaml_data = yaml.safe_load(open(yaml_file if _type == TEST else "tmp/testdir/"+yaml_file, "r"))
            yaml_data = yaml.safe_load(open("tmp/testdir/" + yaml_file, "r"))
        except yaml.YAMLError as err:
            raise JobValidationException(name="YAML Error",
                                         message=f"Invalid YAML file {yaml_file}",
                                         details=err)

        # Validate YAML data with schema
        schema_dir_path = Path("compliance_suite/test_config").absolute()
        test_schema_path = Path("compliance_suite/test_config/test_schema.json")
        template_schema_path = Path("compliance_suite/test_config/template_schema.json")
        schema_file_path = str(test_schema_path if _type == TEST else template_schema_path)
        json_schema = yaml.safe_load(open(schema_file_path, "r"))

        try:
            # Python-jsonschema does not reference local files directly
            # Refer solution from https://github.com/python-jsonschema/jsonschema/issues/98#issuecomment-105475109
            resolver = RefResolver('file:///' + str(schema_dir_path).replace("\\", "/") + '/', None)
            validate(yaml_data, json_schema, resolver=resolver)
            logger.info(f'YAML file valid for {_type}: {yaml_file}')
        except ValidationError as err:
            raise JobValidationException(name="YAML Schema Validation Error",
                                         message=f"YAML file {yaml_file} does not match the {_type} schema",
                                         details=err.message)

        return yaml_data

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
            yaml_data = self.load_and_validate_yaml_data(str(yaml_file), TEST)
            report_phase = self.report.add_phase(str(yaml_file), yaml_data["description"])

            if (self.version in yaml_data["versions"]
                    and tag_matcher(self.include_tags, self.exclude_tags, yaml_data["tags"])):
                test_runner = TestRunner(self.server, self.version)
                job_list: List[Dict] = []
                for job in yaml_data["jobs"]:
                    if "$ref" in job:
                        template_data = self.load_and_validate_yaml_data(job["$ref"], TEMPLATE)
                        if "args" in job:
                            for key, value in job["args"].items():
                                template_data = replace_string(template_data, f"{{{key}}}", value)
                        job_list.extend(template_data)
                    else:
                        job_list.append(job)

                for index, job in enumerate(job_list, start=1):
                    logger.info(f'Running tests for sub-job-{index} -> {job["name"]}')
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
                for yaml_file in sorted(search_path.glob("**/*.yml")):
                    self.initialize_test(yaml_file)

        self.generate_summary()
