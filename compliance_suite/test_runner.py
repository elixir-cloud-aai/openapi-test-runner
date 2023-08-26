"""Module compliance_suite.test_runner.py

This module contains class definition for Test Runner to run the individual jobs, validate them and store their result
"""

import importlib
import json
from pathlib import Path
import re
from typing import (
    Any,
    Dict
)
import yaml

from dotmap import DotMap
from ga4gh.testbed.report.test import Test
from pydantic import ValidationError
from requests.models import Response

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

    def __init__(self, server: str, version: str):
        """Initialize the Test Runner object

        Args:
            server (str): The server URL to send the request
            version (str): The version of the deployed server
        """

        self.server: str = server
        self.version: str = version
        self.job_data: Any = None
        self.auxiliary_space: Dict = {}     # Dictionary to store the sub-job results
        self.report_test: Any = None        # Test object to store the result
        self.api_config: Any = None         # Store API config from Tests Repository
        self.tests_repo_name: str = next(Path("tmp/testdir").iterdir()).name

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

    def set_api_config(self) -> None:
        """Retrieve the API config from Tests Repo and set the api_config"""

        api_config_path = Path("tmp/testdir") / self.tests_repo_name / "api_config.yml"
        try:
            self.api_config = yaml.safe_load(open(api_config_path, "r"))
        except yaml.YAMLError as err:
            raise JobValidationException(name="YAML Error",
                                         message=f"Invalid YAML file {api_config_path}",
                                         details=err)

    def validate_logic(
            self,
            endpoint_model: str,
            json_data: Any,
            message: str
    ) -> None:
        """ Validates if the response is in accordance with the API Specs and Models. Validation is done via
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
            pydantic_module_path = ("tmp.testdir.models.v" + self.version.replace('.', '_') + "_specs")
            pydantic_module: Any = importlib.import_module(pydantic_module_path)
            pydantic_model_name: str = self.api_config["ENDPOINT_TO_MODEL"][endpoint_model]
            pydantic_model_class: Any = getattr(pydantic_module, pydantic_model_name)
            pydantic_model_class(**json_data)  # JSON validation against Pydantic Model
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
            logger.info(f'{self.job_data["operation"]} {self.job_data["endpoint"]} response status code matched')
            ReportUtility.case_pass(case=report_case_status,
                                    message=f'{self.job_data["operation"]} {self.job_data["endpoint"]} Successful '
                                            f'Response status code',
                                    log_message="No logs for success")

        else:
            ReportUtility.case_fail(case=report_case_status,
                                    message=f'Response status code for {self.job_data["operation"]}'
                                            f' {self.job_data["endpoint"]} did not match',
                                    log_message="")

            raise TestFailureException(name="Incorrect HTTP Response Status",
                                       message=f'Response status code for {self.job_data["operation"]}'
                                               f' {self.job_data["endpoint"]} did not match',
                                       details=None)

        # Logical Schema Validation
        if response_status == 200:               # Further response checks only if successful response body
            if not response.text:
                response_json: Any = {}          # Handle the Cancel Task Endpoint empty response
            else:
                response_json: Any = response.json()

            if self.job_data["name"] in ["list_tasks", "get_task"]:
                view_query: str = ""
                for query_param in self.job_data["query_parameters"]:
                    if "view" in query_param:
                        view_query = query_param["view"]
                endpoint_model: str = self.job_data["name"] + "_" + view_query
            else:
                endpoint_model: str = self.job_data["name"]
            self.validate_logic(endpoint_model, response_json, "Response")
            self.validate_filters(response_json)
            self.save_storage_vars(response_json)

    def validate_filters(self, json_data: Any) -> None:
        """Extract the API data key values and compare with the filter value

        Args:
            json_data: The request/response data in JSON format
        """

        if "filter" in self.job_data.keys():
            for index, job_filter in enumerate(self.job_data["filter"], start=1):

                report_case_filter = self.report_test.add_case()
                report_case_result: bool = True
                ReportUtility.set_case(case=report_case_filter,
                                       name=f'Filter-{index}',
                                       description=f'Validate the response against filter-{index}')

                filtered_value: Any = ""   # Retrieve the API data value through DotMap parser
                dot_dict = DotMap(json_data)
                if dot_dict is not None:
                    filtered_value = eval("dot_dict." + job_filter["path"].split('.', maxsplit=1)[1])

                # Check if provided filter type matches with the filtered value class
                if not ((job_filter["type"] == "string" and isinstance(filtered_value, str)) or
                        (job_filter["type"] == "array" and isinstance(filtered_value, list)) or
                        (job_filter["type"] == "object" and isinstance(filtered_value, DotMap))):
                    logger.info(f'Filter-{index} failed due to invalid filter type')
                    ReportUtility.case_fail(case=report_case_filter,
                                            message=f'Filter-{index} failed for {self.job_data["operation"]} '
                                                    f'{self.job_data["endpoint"]} due to invalid filter type',
                                            log_message="")
                    raise JobValidationException(name="Failed filtering",
                                                 message=f'Filter-{index} failed for {self.job_data["operation"]} '
                                                         f'{self.job_data["endpoint"]} due to invalid filter type',
                                                 details=None)

                # Individual data type conditions
                if "value" in job_filter:
                    if job_filter["type"] == "string":
                        if "regex" in job_filter and job_filter["regex"]:
                            report_case_result = bool(re.search(job_filter["value"], filtered_value))
                        else:
                            report_case_result = job_filter["value"] == filtered_value

                    elif job_filter["type"] == "array":
                        report_case_result = job_filter["value"] in filtered_value

                    elif job_filter["type"] == "object":
                        filtered_dict: Dict = filtered_value.toDict()
                        report_case_result = json.loads(job_filter["value"]).items() <= filtered_dict.items()

                # Check size if specified
                if "size" in job_filter:
                    report_case_result = report_case_result and len(filtered_value) == job_filter["size"]

                # Update report case status
                if report_case_result:
                    logger.info(f'Filter-{index} passed')
                    ReportUtility.case_pass(case=report_case_filter,
                                            message=f'Filter-{index} passed for {self.job_data["operation"]} '
                                                    f'{self.job_data["endpoint"]}',
                                            log_message="No logs for success")
                else:
                    logger.info(f'Filter-{index} failed')
                    ReportUtility.case_fail(case=report_case_filter,
                                            message=f'Filter-{index} failed for {self.job_data["operation"]} '
                                                    f'{self.job_data["endpoint"]}',
                                            log_message="")
                    raise TestFailureException(name="Failed filtering",
                                               message=f'Filter-{index} failed for {self.job_data["operation"]} '
                                                       f'{self.job_data["endpoint"]}',
                                               details=None)

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

    def transform_parameters(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Transform the parameters by replacing the storage variables with their exact values.

        Args:
            params: The parameters dictionary to be transformed

        Returns:
            The transformed dictionary after replacing values
        """

        for param in params:
            if str(params[param]).startswith("{") and str(params[param]).endswith("}"):
                storage_key: str = params[param][1:-1]
                if storage_key in self.auxiliary_space:
                    params[param] = self.auxiliary_space[storage_key]
                else:
                    raise JobValidationException(name="Path param not found in storage vars",
                                                 message=f'Param {param} not found in storage vars.'
                                                         f'{self.job_data["operation"]} {self.job_data["endpoint"]}'
                                                         f' failed',
                                                 details=None)
        return params

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

        path_params: Dict = {}
        query_params: Dict = {}
        request_body: str = "{}"

        if "path_parameters" in self.job_data:
            for path_param in self.job_data["path_parameters"]:
                path_params[path_param] = self.job_data["path_parameters"][path_param]
        self.transform_parameters(path_params)

        if "query_parameters" in self.job_data:
            for param in self.job_data["query_parameters"]:
                query_params.update(param)
        self.transform_parameters(query_params)

        if "request_body" in self.job_data:
            request_body: str = self.job_data["request_body"]
            self.validate_request_body(request_body)

        client = Client()
        client.set_request_headers(self.api_config["REQUEST_HEADERS"])

        if "polling" in self.job_data.keys():

            check_cancel: bool = False
            if "env_vars" in self.job_data.keys() and "check_cancel" in self.job_data["env_vars"].keys():
                check_cancel = self.job_data["env_vars"]["check_cancel"]

            response = client.poll_request(server=self.server, version=self.version,
                                           endpoint=self.job_data["endpoint"], path_params=path_params,
                                           query_params=query_params, operation=self.job_data["operation"],
                                           polling_interval=self.job_data["polling"]["interval"],
                                           polling_timeout=self.job_data["polling"]["timeout"],
                                           check_cancel_val=check_cancel)
        else:
            response = client.send_request(server=self.server, version=self.version,
                                           endpoint=self.job_data["endpoint"], path_params=path_params,
                                           query_params=query_params, operation=self.job_data["operation"],
                                           request_body=request_body)

        self.validate_response(response)
