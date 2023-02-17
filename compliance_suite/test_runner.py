"""Module compliance_suite.test_runner.py

This module contains class definition for Test Runner to run the individual jobs, validate them and store their result
"""

import json
from typing import (
    Any,
    Dict,
    List
)

from dotmap import DotMap
from ga4gh.testbed.report.test import Test
from pydantic import ValidationError
from requests.models import Response

from compliance_suite.constants.constants import ENDPOINT_TO_MODEL
from compliance_suite.exceptions.compliance_exception import (
    JobValidationException,
    TestFailureException
)
from compliance_suite.functions.client import Client
from compliance_suite.functions.log import logger
from compliance_suite.functions.report import ReportUtility


class TestRunner():
    """Class to run individual jobs by sending requests to the server endpoints. It stores the data to be used by other
    jobs. It validates the request, response and their schemas"""

    def __init__(self, service: str, server: str, version: str):
        """Initialize the Test Runner object

        Args:
            service (str): The GA4GH service name (eg. TES)
            server (str): The server URL to send the request
            version (str): The version of the deployed server
        """

        self.service: str = service
        self.server: str = server
        self.version: str = version
        self.job_data: Any = None
        self.auxiliary_space: Dict = {}     # Dictionary to store the sub-job results
        self.report_test: Any = None        # Test object to store the result

    def set_job_data(self, job_data: Any) -> None:
        """Set the individual sub job data

        Args:
            job_data (Any): The parsed job data containing the sub-job details
        """

        self.job_data = job_data

    def set_auxiliary_space(self, key: str, value: Any) -> None:
        """Insert a key-value pair inside the auxiliary space

        Args:
            key (str): The key name for auxiliary_space dict
            value (Any): The parsed response JSON data for auxiliary_space dict
        """

        self.auxiliary_space[key] = value

    def set_report_test(self, report_test: Test) -> None:
        """Set the test object for use inside the class

        Args:
            report_test (Test): The test object to store the result
        """

        self.report_test = report_test

    def validate_logic(
            self,
            endpoint_model: str,
            json_data: Any,
            message: str
    ) -> None:
        """ Validates if the response is in accordance with the TES API Specs and Models. Validation is done via
        Pydantic generated models

        Args:
            endpoint_model (str): The endpoint name for mapping the Model class
            json_data (Any): The response JSON data which will be checked for schema validation
            message (str): Message specifying if it is a request or a response
        """

        report_case_schema = self.report_test.add_case()
        ReportUtility.set_case(case=report_case_schema,
                               name=f"{message.lower()}_schema_validation",
                               description="Check if response matches the model schema")

        try:
            ENDPOINT_TO_MODEL[endpoint_model](**json_data)
            logger.info(f'{message} Schema validation successful for '
                        f'{self.job_data["operation"]} {self.job_data["endpoint"]}')
            ReportUtility.case_pass(case=report_case_schema,
                                    message=f'{message} Schema validation successful for {self.job_data["operation"]} '
                                            f'{self.job_data["endpoint"]}',
                                    log_message="No logs for success")
        except ValidationError as err:
            ReportUtility.case_fail(case=report_case_schema,
                                    message=f'{message} Schema validation failed for {self.job_data["operation"]}'
                                            f' {self.job_data["endpoint"]}',
                                    log_message=err.__str__())
            raise TestFailureException(name="Schema Validation Error",
                                       message=f'{message} Schema validation failed for {self.job_data["operation"]}'
                                               f' {self.job_data["endpoint"]}',
                                       details=err)

    def validate_request_body(
            self,
            request_body: str
    ) -> None:
        """ Validates the request body for proper JSON format. Validates the request body with respective
        API Model

        Args:
            request_body (str): The request body from the YAML test file
        """

        report_case_json_check = self.report_test.add_case()
        ReportUtility.set_case(case=report_case_json_check,
                               name="request_body_json_validation",
                               description="Check if request body is in proper JSON format")

        # JSON Validation
        try:
            request_body_json: Any = json.loads(request_body)
            ReportUtility.case_pass(case=report_case_json_check,
                                    message=f'Proper JSON format in request body for {self.job_data["operation"]}'
                                            f' {self.job_data["endpoint"]}',
                                    log_message="No logs for success")
        except json.JSONDecodeError as err:
            ReportUtility.case_fail(case=report_case_json_check,
                                    message=f'JSON Error in request body for {self.job_data["operation"]}'
                                            f' {self.job_data["endpoint"]}',
                                    log_message=err.__str__())
            raise JobValidationException(name="JSON Decode Error",
                                         message=f'JSON Error in request body for {self.job_data["operation"]}'
                                                 f' {self.job_data["endpoint"]}',
                                         details=err)

        # Logical Schema Validation

        endpoint_model: str = self.job_data["name"] + "_request_body"
        self.validate_logic(endpoint_model, request_body_json, "Request Body")
        self.save_storage_vars(request_body_json)

    def validate_response(
            self,
            response: Response
    ) -> None:
        """ Validates the response status. Validates the response with respective API Model. Stores the data in the
        auxiliary space

        Args:
            response (Response): The JSON response obtained from client.py
        """

        # General status validation
        response_status: int = int(list(self.job_data["response"].keys())[0])

        report_case_status = self.report_test.add_case()
        ReportUtility.set_case(case=report_case_status,
                               name="status_code",
                               description="Check if response status code is 200")

        if response.status_code == response_status:
            logger.info(f'{self.job_data["operation"]} {self.job_data["endpoint"]} Successful Response status code')
            ReportUtility.case_pass(case=report_case_status,
                                    message=f'{self.job_data["operation"]} {self.job_data["endpoint"]} Successful '
                                            f'Response status code',
                                    log_message="No logs for success")

        else:
            ReportUtility.case_fail(case=report_case_status,
                                    message=f'Unsuccessful Response status code for '
                                            f'{self.job_data["operation"]} {self.job_data["endpoint"]}',
                                    log_message="")

            raise TestFailureException(name="Incorrect HTTP Response Status",
                                       message=f'{self.job_data["operation"]} {self.job_data["endpoint"]} '
                                               f'Response status code is not 200',
                                       details=None)

        # Logical Schema Validation
        if not response.text:
            response_json: Any = {}          # Handle the Cancel Task Endpoint empty response
        else:
            response_json: Any = response.json()

        if self.job_data["name"] in ["list_tasks", "get_task"]:
            view_query: List[str] = [item["view"] for item in self.job_data["query_parameters"]]
            endpoint_model: str = self.job_data["name"] + "_" + view_query[0]
        else:
            endpoint_model: str = self.job_data["name"]
        self.validate_logic(endpoint_model, response_json, "Response")
        self.save_storage_vars(response_json)

    def save_storage_vars(self, json_data: Any) -> None:
        """ Extract the keys mentioned in the YAML job from the request/response and save them in the auxiliary space.

        Args:
            json_data (Any): The request/response data in JSON format
        """

        if "storage_vars" in self.job_data.keys():
            dot_dict = DotMap(json_data)
            if dot_dict is not None:
                for key, value in self.job_data["storage_vars"].items():
                    # Default value of absent key is DotMap()
                    if key not in self.auxiliary_space.keys() or self.auxiliary_space[key] == "DotMap()":
                        dot_value = str(eval("dot_dict." + value.split('.', maxsplit=1)[1]))
                        self.set_auxiliary_space(key, dot_value)

    def run_tests(
            self,
            job_data: Any,
            report_test: Test
    ) -> None:
        """ Runs the individual jobs

        Args:
            job_data (Any): The parsed YAML sub-job data containing information for test
            report_test (Test): The test object to store the result
        """

        self.set_job_data(job_data)
        ReportUtility.set_test(test=report_test,
                               name=job_data["name"],
                               description=job_data["description"])
        self.set_report_test(report_test)

        uri_params: Dict = {}
        query_params: Dict = {}
        request_body: str = "{}"

        if self.job_data["name"] in ["get_task", "cancel_task"]:
            uri_params["id"] = self.auxiliary_space["id"]

        if self.job_data["name"] in ["get_task", "list_tasks"]:
            for param in self.job_data["query_parameters"]:
                query_params.update(param)

        if self.job_data["name"] in ["create_task"]:
            request_body: str = self.job_data["request_body"]
            self.validate_request_body(request_body)

        client = Client()

        if "polling" in self.job_data.keys():

            check_cancel: bool = False
            if "env_vars" in self.job_data.keys() and "check_cancel" in self.job_data["env_vars"].keys():
                check_cancel = self.job_data["env_vars"]["check_cancel"]

            response = client.poll_request(service=self.service, server=self.server, version=self.version,
                                           endpoint=self.job_data["endpoint"], uri_params=uri_params,
                                           query_params=query_params, operation=self.job_data["operation"],
                                           polling_interval=self.job_data["polling"]["interval"],
                                           polling_timeout=self.job_data["polling"]["timeout"],
                                           check_cancel_val=check_cancel)
        else:
            response = client.send_request(service=self.service, server=self.server, version=self.version,
                                           endpoint=self.job_data["endpoint"], uri_params=uri_params,
                                           query_params=query_params, operation=self.job_data["operation"],
                                           request_body=request_body)

        self.validate_response(response)
