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
    TestFailureException
)
from compliance_suite.functions.log import logger
from compliance_suite.test_runner import TestRunner


class JobRunner():
    """Class to run the individual YAML Tests"""

    def __init__(self, tags):
        self.path: str = os.getcwd()
        self.tags: List[str] = tags
        self.test_count: int = 0
        self.test_status: Dict = {        # To store the status of each test
            "passed": [],
            "failed": [],
            "skipped": []
        }

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
            yaml_file: str
    ) -> None:
        """ Validates if the Test file is in conformance to the test template/schema"""

        schema_path: str = os.path.join(self.path, "../tests", "template", "test_template_schema.json")
        with open(schema_path, "r") as f:
            json_schema: Any = yaml.safe_load(f)

        try:
            validate(yaml_data, json_schema)
            logger.info(f'Test YAML file valid for {yaml_file}')
        except ValidationError as err:
            raise JobValidationException(name="YAML Schema Validation Error",
                                         message=f"YAML file {yaml_file} does not match the Test template/schema",
                                         details=err.message)

    def tag_matcher(
            self,
            yaml_tags: List[str]
    ) -> bool:
        """ Checks if any user provided tags match with the YAML Testfile tags. Skips the test if tag not matched """

        for user_tag in self.tags:
            if user_tag in yaml_tags:
                return True
        return False

    def run_jobs(self) -> None:
        """ Reads the Test files from compliance-suite-tests directory. Validates and parses individual jobs.
        The individual jobs are then executed via Test Runner"""

        os.chdir(os.getcwd())
        yaml_path: Any = os.path.join(self.path, "..", "tests")
        for yaml_file in os.listdir(yaml_path):
            if yaml_file.endswith(".yml"):
                self.test_count += 1
                logger.log(LOGGING_LEVEL['SUMMARY'], "\n{:#^100}".format(f"     Initiating Test-{self.test_count}"
                                                                         f" for {yaml_file}     "))
                yaml_data: Any = None
                try:
                    with open(os.path.join(yaml_path, yaml_file), "r") as f:
                        try:
                            yaml_data = yaml.safe_load(f)
                        except yaml.YAMLError as err:
                            raise JobValidationException(name="YAML Error",
                                                         message=f"Invalid YAML file {yaml_file}",
                                                         details=err)
                    self.validate_job(yaml_data, yaml_file)

                    if self.tag_matcher(yaml_data["tags"]):
                        test_runner = TestRunner(yaml_data["service"], yaml_data["server"],
                                                 yaml_data["version"][0])
                        job_count: int = 0
                        for job in yaml_data["jobs"]:
                            job_count += 1
                            logger.info(f'Running tests for sub-job-{job_count} -> {job["name"]}')
                            test_runner.run_tests(job)
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

        self.generate_summary()
