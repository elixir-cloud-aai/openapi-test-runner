"""Module compliance_suite.functions.report.py

This module contains class definition for Report which will generate the report from each test case
"""

from typing import Any

from ga4gh.testbed.report.report import Report as ReportBuilder


class Report():
    """Class to generate the report and handle the internal tests and cases"""

    def __init__(self):
        """Initialize the Report object"""

        self.platform_name = ""
        self.report = ReportBuilder()   # Object from the ga4gh-tested-lib

        self.initialize_report()

    def initialize_report(self) -> None:
        """Set Testbed Report details"""

        self.report.set_testbed_name("TES Compliance Suite")
        self.report.set_testbed_version("0.1.0")
        self.report.set_testbed_description("TES Compliance Suite tests the platform against the GA4GH TES API "
                                            "specs. Its an automated tool system testing against YAML-based test "
                                            "files along with the ability to validate cloud service/functionality.")

    def set_platform_details(self, platform_server: str) -> None:
        """Set Platform Report details

        Args:
            platform_server (str): The server URL of the platform on which compliance tested is done
        """

        self.platform_name = platform_server
        self.report.set_platform_name(platform_server)
        self.report.set_platform_description(f"TES service deployed on the {platform_server}")

    def add_phase(self, filename: str, description: str) -> Any:
        """Add a phase which is individual YAML test file

        Args:
            filename (str): The YAML Testfile name. The phase will be identified via this name.
            description: The YAML Testfile description for a more detailed explanation.

        Returns:
            (Any): Returns a new phase object
        """

        phase = self.report.add_phase()
        phase.set_phase_name(f"{filename}")
        phase.set_phase_description(description)
        return phase

    def generate(self) -> Any:
        """Calculate the statuses and generate a JSON report

        Returns:
            (Any): Returns the final JSON report in pretty format
        """

        self.report.finalize()
        return self.report.to_json(True)


class ReportUtility():
    """Utility class for Report to set the tests and cases"""

    @staticmethod
    def trunc(log_message: str) -> str:
        """Truncate the log messages if the length is more than 150 chars

        Args:
            log_message (str): The log message to be truncated

        Returns:
            (str): The truncated log message
        """

        if len(log_message) > 150:
            return log_message[1:150] + "..."
        else:
            return log_message

    @staticmethod
    def set_case(case: Any, name: str, description: str) -> None:
        """Set the case details

        Args:
            case (Any): The case object to set the case details
            name (str): The case name
            description (str): The case description
        """

        case.set_case_name(name)
        case.set_case_description(description)

    @staticmethod
    def set_test(test: Any, name: str, description: str) -> None:
        """Set the test details

        Args:
            test (Any): The test object to set the test details
            name (str): The test name
            description (str): The test description
        """

        test.set_test_name(name)
        test.set_test_description(description)

    @staticmethod
    def case_pass(case: Any, message: str, log_message: str) -> None:
        """Update the case details with Passed

        Args:
            case (Any): The case object to set the case details
            message (str): The case message containing the case summary
            log_message (str): The case log messages for further case details
        """

        case.set_status_pass()
        case.set_message(message)
        case.add_log_message(ReportUtility.trunc(log_message))

    @staticmethod
    def case_fail(case: Any, message: str, log_message: str) -> None:
        """Update the case details with Failed

        Args:
            case (Any): The case object to set the case details
            message (str): The case message containing the case summary
            log_message (str): The case log messages for further case details
        """

        case.set_status_fail()
        case.set_message(message)
        case.add_log_message(ReportUtility.trunc(log_message))
