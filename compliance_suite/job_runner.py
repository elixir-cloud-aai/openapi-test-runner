"""Module compliance_suite.job_runner.py

This module contains class definition for Job Runner to run the individual YAML Tests from compliance-suite-tests
directory
"""

import os
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

from compliance_suite.constants.constants import LOGGING_LEVEL
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


class JobRunner():
    """Class to run the individual YAML Tests"""

    def __init__(self, tags: List[str]):
        """Initialize the Job Runner object

        Args:
            tags (List[str]): The list of tags for which the compliance suite will be run
        """

        self.path: str = os.getcwd()
        self.tags: List[str] = tags
        self.test_count: int = 0
        self.test_status: Dict = {        # To store the status of each test
            "passed": [],
            "failed": [],
            "skipped": []
        }
        self.report: Any = None

    def set_report(self, report: Any) -> None:
        """Set the report data member

        Args:
            report (Any): The report object to be defined for use inside the class
        """
        self.report = report

    def generate_summary(self) -> None:
        """Generate test summary at the completion"""

        passed_tests: str = ", ".join(self.test_status["passed"])
        failed_tests: str = ", ".join(self.test_status["failed"])
        skipped_tests: str = ", ".join(self.test_status["skipped"])
        passed_tests_count: int = len(self.test_status["passed"])
        failed_tests_count: int = len(self.test_status["failed"])
        skipped_tests_count: int = len(self.test_status["skipped"])

        logger.log(LOGGING_LEVEL['SUMMARY'], "\n\n\n")
        logger.log(LOGGING_LEVEL['SUMMARY'], "{:#^90}".format("   Compliance Testing Summary   "))
        logger.log(LOGGING_LEVEL['SUMMARY'], "#{:^88}#".format(""))
        logger.log(LOGGING_LEVEL['SUMMARY'], "#{:^88}#".format(f"Total Tests - {self.test_count}"))
        logger.log(LOGGING_LEVEL['SUMMARY'], "#{:^88}#".format(f'Passed - {passed_tests_count} ({passed_tests})'))
        logger.log(LOGGING_LEVEL['SUMMARY'], "#{:^88}#".format(f'Failed - {failed_tests_count} ({failed_tests})'))
        logger.log(LOGGING_LEVEL['SUMMARY'], "#{:^88}#".format(f'Skipped - {skipped_tests_count} ({skipped_tests})'))
        logger.log(LOGGING_LEVEL['SUMMARY'], "#{:^88}#".format(""))
        logger.log(LOGGING_LEVEL['SUMMARY'], "{:#^90}".format(""))

    def validate_job(
            self,
            yaml_data: Any,
            yaml_file: str,
            report_case_yaml_validate: Any
    ) -> None:
        """ Validates if the Test file is in conformance to the test template/schema

        Args:
            yaml_data (Any): The parsed yaml data to perform the schema checks
            yaml_file (str): The yaml file name
            report_case_yaml_validate (Any): The test case object to populate the result for YAML schema check
        """

        schema_path: str = os.path.join(self.path, "tests", "template", "test_template_schema.json")
        with open(schema_path, "r") as f:
            json_schema: Any = yaml.safe_load(f)

        try:
            validate(yaml_data, json_schema)
            logger.info(f'Test YAML file valid for {yaml_file}')
            ReportUtility.case_pass(case=report_case_yaml_validate,
                                    message=f'Test YAML file valid for {yaml_file}',
                                    log_message="No logs for success")
        except ValidationError as err:
            ReportUtility.case_fail(case=report_case_yaml_validate,
                                    message=f'YAML file {yaml_file} does not match the Test template/schema',
                                    log_message=err.message)
            raise JobValidationException(name="YAML Schema Validation Error",
                                         message=f"YAML file {yaml_file} does not match the Test template/schema",
                                         details=err.message)

    def tag_matcher(
            self,
            yaml_tags: List[str]
    ) -> bool:
        """ Checks if any user provided tags match with the YAML Testfile tags. Skips the test if tag not matched

        Args:
            yaml_tags (List[str]): The tags defined for a YAML test file

        Returns:
            (bool): If the user tags match the YAML test file tags, return True
        """

        for user_tag in self.tags:
            if user_tag in yaml_tags:
                return True
        return False

    def generate_report(self) -> Any:
        """Generates the report via ga4gh-testbed-lib and returns it

        Return:
            (Any): Returns the JSON compliance report
        """

        json_report = self.report.generate()
        return json_report

    def run_jobs(self) -> None:
        """ Reads the Test files from compliance-suite-tests directory. Validates and parses individual jobs.
        The individual jobs are then executed via Test Runner"""

        os.chdir(os.getcwd())

        report = Report()
        self.set_report(report)

        yaml_path: Any = os.path.join(self.path, "tests")
        for yaml_file in os.listdir(yaml_path):
            if yaml_file.endswith(".yml"):
                self.test_count += 1
                logger.log(LOGGING_LEVEL['SUMMARY'], "\n{:#^100}".format(f"     Initiating Test-{self.test_count}"
                                                                         f" for {yaml_file}     "))

                report_phase = self.report.add_phase(yaml_file.split("/")[-1])
                report_yaml_test = report_phase.add_test()
                ReportUtility.set_test(test=report_yaml_test,
                                       name="yaml_test",
                                       description="Perform tests on YAML Test File")
                yaml_data: Any = None
                report_job_test: Any = None
                try:

                    report_case_yaml = report_yaml_test.add_case()
                    ReportUtility.set_case(case=report_case_yaml,
                                           name="yaml_check",
                                           description="Check if YAML file is in proper format")

                    with open(os.path.join(yaml_path, yaml_file), "r") as f:
                        try:
                            yaml_data = yaml.safe_load(f)
                            ReportUtility.case_pass(case=report_case_yaml,
                                                    message=f'Proper YAML format for {yaml_file}',
                                                    log_message="No logs for success")
                        except yaml.YAMLError as err:
                            ReportUtility.case_fail(case=report_case_yaml,
                                                    message=f'Invalid YAML file {yaml_file}',
                                                    log_message=err.__str__())
                            raise JobValidationException(name="YAML Error",
                                                         message=f"Invalid YAML file {yaml_file}",
                                                         details=err)

                    report_case_yaml_validate = report_yaml_test.add_case()
                    ReportUtility.set_case(case=report_case_yaml_validate,
                                           name="yaml_validate",
                                           description="Validate if YAML file is in proper schema")
                    self.validate_job(yaml_data, yaml_file, report_case_yaml_validate)

                    if self.report.platform_name == "":
                        self.report.set_platform_details(yaml_data["server"])

                    if self.tag_matcher(yaml_data["tags"]):
                        test_runner = TestRunner(yaml_data["service"], yaml_data["server"],
                                                 yaml_data["version"][0])
                        job_count: int = 0
                        for job in yaml_data["jobs"]:
                            job_count += 1
                            logger.info(f'Running tests for sub-job-{job_count} -> {job["name"]}')
                            report_job_test = report_phase.add_test()
                            test_runner.run_tests(job, report_job_test)
                        self.test_status["passed"].append(str(self.test_count))
                        logger.log(LOGGING_LEVEL['SUCCESS'], f'Compliance Test-{self.test_count}'
                                                             f' for {yaml_file} successful.')
                    else:
                        self.test_status["skipped"].append(str(self.test_count))
                        logger.log(LOGGING_LEVEL['SKIP'], f"No Tag matched. Skipping Test-{self.test_count}"
                                                          f" for {yaml_file}")

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

        self.generate_summary()
