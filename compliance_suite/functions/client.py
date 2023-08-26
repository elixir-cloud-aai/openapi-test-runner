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

from compliance_suite.exceptions.compliance_exception import (
    TestFailureException,
    TestRunnerException
)
from compliance_suite.functions.log import logger


class Client():
    """ This class is used to send REST requests to the provided server URL """

    def __init__(self):
        """ Initialize the Client object"""

        self.check_cancel = False   # Checks if the Cancel status is to be validated or not
        self.request_headers: Dict = {}

    def set_request_headers(self, request_headers) -> None:
        """ Sends the REST request to provided server

            Args:
                request_headers: The request headers extracted from Tests repo API config
        """

        self.request_headers = request_headers

    def send_request(
            self,
            server: str,
            version: str,
            endpoint: str,
            path_params: Dict,
            query_params: Dict,
            operation: str,
            request_body: str
    ) -> Response:
        """ Sends the REST request to provided server

        Args:
            server (str): The server URL to send the request
            version (str): The version of the deployed server
            endpoint (str): The endpoint of the given server
            path_params (dict): URI parameters in the endpoint
            query_params (dict): The query parameters to be sent along with the request
            operation (str): The HTTP operation for the endpoint
            request_body (str): The request body for the request

        Returns:
            (Response): The response from the server is returned
        """

        for key in path_params.keys():
            endpoint = endpoint.replace(f"{{{key}}}", path_params[key])

        version = "v" + version.split(".")[0]  # Convert SemVer into Major API version
        base_url: str = str(server) + version + endpoint
        response = None
        logger.info(f"Sending {operation} request to {base_url}. Query Parameters - {query_params}")
        try:
            if operation == "GET":
                response = requests.get(base_url, headers=self.request_headers, params=query_params)
            elif operation == "POST":
                request_body = json.loads(request_body)
                response = requests.post(base_url, headers=self.request_headers, json=request_body)
            return response
        except OSError as err:
            raise TestRunnerException(name="OS Error",
                                      message=f"Connection error to {operation} {base_url}",
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
        valid_states = ["CANCELED", "CANCELING"] if self.check_cancel else ["COMPLETE", "EXECUTOR_ERROR",
                                                                            "SYSTEM_ERROR", "PREEMPTED"]
        if response_json["state"] in valid_states:
            logger.info("Expected response received. Polling request successful")
            return True

        logger.info("Unexpected response from Polling request. Retrying...")
        return False

    def poll_request(
            self,
            server: str,
            version: str,
            endpoint: str,
            path_params: Dict,
            query_params: Dict,
            operation: str,
            polling_interval: int,
            polling_timeout: int,
            check_cancel_val: bool
    ) -> Response:
        """ This function polls a request to specified server with given interval and timeout

        Args:
            server (str): The server URL to send the request
            version (str): The version of the deployed server
            endpoint (str): The endpoint of the given server
            path_params (dict): URI parameters in the endpoint
            query_params (dict): The query parameters to be sent along with the request
            operation (str): The HTTP operation for the endpoint
            polling_interval (int): The duration between polling
            polling_timeout (int): The timeout for the polling request. Raises Timeout exception if exceeded
            check_cancel_val (bool): Bool to verify Cancel status or not

        Returns:
            (Response): The response from the server is returned
        """

        for key in path_params.keys():
            endpoint = endpoint.replace(f"{{{key}}}", path_params[key])

        self.check_cancel = check_cancel_val
        version = "v" + version.split(".")[0]  # Convert SemVer into Major API version
        base_url: str = str(server) + version + endpoint

        logger.info(f"Sending {operation} polling request to {base_url}. Query Parameters - {query_params}")

        try:
            response = polling2.poll(lambda: requests.get(base_url, headers=self.request_headers, params=query_params),
                                     step=polling_interval, timeout=polling_timeout,
                                     check_success=self.check_poll)
            return response
        except polling2.TimeoutException:
            raise TestFailureException(name="Polling Timeout Exception",
                                       message=f"Polling timeout for {operation} {base_url}",
                                       details=None)
        except OSError as err:
            raise TestRunnerException(name="OS Error",
                                      message=f"Connection error to {operation} {base_url}",
                                      details=err)
