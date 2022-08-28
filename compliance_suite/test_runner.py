"""Module compliance_suite.test_runner.py

This module contains class definition for Test Runner to run the individual jobs, validate them and store their result
"""

import json
from typing import (
    Any,
    Dict,
    List
)

from pydantic import ValidationError
from requests.models import Response

from compliance_suite.functions.log import logger
from compliance_suite.constants.constants import (
    ENDPOINT_TO_MODEL,
    VERSION_INFO,
)
from compliance_suite.functions.client import Client
from compliance_suite.exceptions.compliance_exception import (
    JobValidationException,
    TestFailureException
)


class TestRunner():
    """Class to run individual jobs by sending requests to the server endpoints. It stores the data to be used by other
    jobs. It validates the request, response and their schemas"""

    def __init__(self, service, server, version):

        self.service: str = service
        self.server: str = server
        self.version: str = VERSION_INFO[version]
        self.job_data: Any = None
        self.auxiliary_space: Dict = {}

    def set_job_data(self, job_data):
        self.job_data = job_data

    def set_auxiliary_space(self, key, value):
        self.auxiliary_space[key] = value

    def validate_logic(
            self,
            endpoint_model: str,
            json_data: Any,
            message: str
    ) -> None:
        """ Validates if the response is in accordance with the TES API Specs and Models. Validation is done via
        Pydantic generated models"""

        try:
            ENDPOINT_TO_MODEL[endpoint_model](**json_data)
            logger.info(f'{message} Schema validation successful for '
                        f'{self.job_data["operation"]} {self.job_data["endpoint"]}')
        except ValidationError as err:
            raise TestFailureException(name="Schema Validation Error",
                                       message=f'{message} Schema validation failed for {self.job_data["operation"]}'
                                               f' {self.job_data["endpoint"]}',
                                       details=err)

    def validate_request_body(
            self,
            request_body: str
    ) -> None:
        """ Validates the request body for proper JSON format. Validates the request body with respective
        API Model"""

        # JSON Validation
        try:
            request_body_json: Any = json.loads(request_body)
        except json.JSONDecodeError as err:
            raise JobValidationException(name="JSON Decode Error",
                                         message=f'JSON Error in request body for {self.job_data["operation"]}'
                                                 f' {self.job_data["endpoint"]}',
                                         details=err)

        # Logical Schema Validation

        endpoint_model: str = self.job_data["name"] + "_request_body"
        self.validate_logic(endpoint_model, request_body_json, "Request Body")

    def validate_response(
            self,
            response: Response
    ) -> None:
        """ Validates the response status. Validates the response with respective API Model. Stores the data in the
        auxiliary space"""

        # General status validation
        response_status: int = list(self.job_data["response"].keys())[0]

        if response.status_code == response_status:
            logger.info(f'{self.job_data["operation"]} {self.job_data["endpoint"]} Successful Response status code')
        else:
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
        self.set_auxiliary_space(self.job_data["name"], response_json)

    def run_tests(
            self,
            job_data: Any
    ) -> None:
        """ Runs the individual jobs """

        self.set_job_data(job_data)

        uri_params: Dict = {}
        query_params: Dict = {}
        request_body: str = "{}"

        if self.job_data["name"] in ["get_task", "cancel_task"]:
            uri_params["id"] = self.auxiliary_space["create_task"]["id"]

        if self.job_data["name"] in ["get_task", "list_tasks"]:
            for param in self.job_data["query_parameters"]:
                query_params.update(param)

        if self.job_data["name"] in ["create_task"]:
            request_body: str = self.job_data["request_body"]
            self.validate_request_body(request_body)

        client = Client()

        if "polling" in self.job_data.keys():

            check_cancel: bool = False
            if "cancel_task" in self.auxiliary_space.keys():
                check_cancel = True

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
