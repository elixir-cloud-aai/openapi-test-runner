"""Module compliance_suite.functions.client.py

This module contains class definition for client to send the requests to the server
"""

import json
from typing import (
    Any,
    Dict
)

import polling2
import requests
from requests.models import Response

from compliance_suite.constants.constants import REQUEST_HEADERS
from compliance_suite.exceptions.compliance_exception import (
    TestFailureException,
    TestRunnerException
)
from compliance_suite.functions.log import logger


class Client():
    """ This class is used to send REST requests to the provided server URL """

    def __init__(self, service: str, server: str, version: str):
        """ Initialize the Client object containing the server details

        Args:
            service: The API service name
            server: The server URL to send the request
            version: The version of the deployed API service
        """

        self.service: str = service
        self.server: str = server
        self.version: str = self.parse_version(version)
        self.request_headers: dict = REQUEST_HEADERS[service]
        self.endpoint: str = ""
        self.uri_params: Dict = {}
        self.query_params: Dict = {}
        self.operation: str = ""
        self.request_body: str = ""
        self.base_url: str = ""
        self.check_cancel = False   # Checks if the Cancel status is to be validated or not

    @staticmethod
    def parse_version(version: str) -> str:
        """Parse the API version and convert into server URL specific version

        Args:
            version: The API version. Format - SemVer

        Returns:
            Transformed version to be set in API server URL
        """

        # Extract the major API version
        return "v" + version.split(".")[0]

    def set_endpoint_data(
            self,
            endpoint: str,
            uri_params: Dict,
            query_params: Dict,
            operation: str,
            request_body: str
    ) -> None:
        """Sets the endpoint data

        Args:
            endpoint: The endpoint of the given server
            uri_params: URI parameters in the endpoint
            query_params: The query parameters to be sent along with the request
            operation: The HTTP operation for the endpoint
            request_body: The request body for the request
        """

        for key in uri_params.keys():
            endpoint = endpoint.replace(f"{{{key}}}", uri_params[key])
        self.endpoint = endpoint
        self.base_url = str(self.server) + self.version + self.endpoint
        self.uri_params = uri_params
        self.query_params = query_params
        self.operation = operation
        self.request_body = request_body

    def send_request(self) -> Response:
        """ Sends the REST request to configured server
        Returns:
            The response from the server is returned
        """

        response = None
        logger.info(f"Sending {self.operation} request to {self.base_url}. Query Parameters - {self.query_params}")
        try:
            if self.operation == "GET":
                response = requests.get(self.base_url, headers=self.request_headers, params=self.query_params)
            elif self.operation == "POST":
                request_body = json.loads(self.request_body)
                response = requests.post(self.base_url, headers=self.request_headers, json=request_body)
            return response
        except OSError as err:
            raise TestRunnerException(name="OS Error",
                                      message=f"Connection error to {self.operation} {self.base_url}",
                                      details=err)

    def check_poll(
            self,
            response: Any
    ) -> bool:
        """ Polling callback function to validate the polling response

        Args:
            response (Any): The polling response that the callback receives

        Returns:
            (bool): Depending on the below checks, return if the response was successful or not
        """

        if response.status_code != 200:
            logger.info("Unexpected response from Polling request. Retrying...")
            return False

        response_json: Any = response.json()
        if self.check_cancel and response_json["state"] in ["CANCELED"]:
            logger.info("Expected response received. Polling request successful")
            return True

        elif not self.check_cancel and response_json["state"] in ["COMPLETE", "EXECUTOR_ERROR", "SYSTEM_ERROR"]:
            logger.info("Expected response received. Polling request successful")
            return True

        logger.info("Unexpected response from Polling request. Retrying...")
        return False

    def poll_request(
            self,
            polling_interval: int,
            polling_timeout: int,
            check_cancel_val: bool
    ) -> Response:
        """ This function polls a request to configured server with given interval and timeout

        Args:
            polling_interval: The duration between polling
            polling_timeout: The timeout for the polling request. Raises Timeout exception if exceeded
            check_cancel_val: Bool to verify Cancel status or not

        Returns:
            The response from the server is returned
        """

        self.check_cancel = check_cancel_val
        logger.info(f"Sending {self.operation} polling request to {self.base_url}."
                    f" Query Parameters - {self.query_params}")

        try:
            response = polling2.poll(
                lambda: requests.get(self.base_url, headers=self.request_headers, params=self.query_params),
                step=polling_interval, timeout=polling_timeout, check_success=self.check_poll
            )
            return response
        except polling2.TimeoutException:
            raise TestFailureException(name="Polling Timeout Exception",
                                       message=f"Polling timeout for {self.operation} {self.base_url}",
                                       details=None)
        except OSError as err:
            raise TestRunnerException(name="OS Error",
                                      message=f"Connection error to {self.operation} {self.base_url}",
                                      details=err)
