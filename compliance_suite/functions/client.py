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

    def __init__(self):
        self.check_cancel = False

    def send_request(
            self,
            service: str,
            server: str,
            version: str,
            endpoint: str,
            uri_params: Dict,
            query_params: Dict,
            operation: str,
            request_body: str
    ) -> Response:
        """ Sends the REST request to provided server"""

        for key in uri_params.keys():
            endpoint = endpoint.replace(f"{{{key}}}", uri_params[key])

        base_url: str = str(server) + version + endpoint
        request_headers: dict = REQUEST_HEADERS[service]
        response = None
        logger.info(f"Sending {operation} request to {base_url}. Query Parameters - {query_params}")
        try:
            if operation == "GET":
                response = requests.get(base_url, headers=request_headers, params=query_params)
            elif operation == "POST":
                request_body = json.loads(request_body)
                response = requests.post(base_url, headers=request_headers, json=request_body)
            return response
        except OSError as err:
            raise TestRunnerException(name="OS Error",
                                      message=f"Connection error to {operation} {base_url}",
                                      details=err)

    def check_poll(
            self,
            response: Any
    ) -> bool:
        """ Polling callback function to validate the polling response"""

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
            service: str,
            server: str,
            version: str,
            endpoint: str,
            uri_params: Dict,
            query_params: Dict,
            operation: str,
            polling_interval: int,
            polling_timeout: int,
            check_cancel_val: bool
    ) -> Response:
        """ This function polls a request to specified server with given interval and timeout"""

        for key in uri_params.keys():
            endpoint = endpoint.replace(f"{{{key}}}", uri_params[key])
        self.check_cancel = check_cancel_val
        base_url: str = str(server) + version + endpoint
        request_headers: dict = REQUEST_HEADERS[service]

        logger.info(f"Sending {operation} polling request to {base_url}. Query Parameters - {query_params}")

        try:
            response = polling2.poll(lambda: requests.get(base_url, headers=request_headers, params=query_params),
                                     step=polling_interval, timeout=polling_timeout,
                                     check_success=self.check_poll)
        except polling2.TimeoutException:
            raise TestFailureException(name="Polling Timeout Exception",
                                       message=f"Polling timeout for {operation} {base_url}",
                                       details=None)
        except OSError as err:
            raise TestRunnerException(name="OS Error",
                                      message=f"Connection error to {operation} {base_url}",
                                      details=err)

        return response
