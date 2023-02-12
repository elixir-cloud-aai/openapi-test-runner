"""Module unittests.test_functions.py

This module is to test the project functions
"""

import unittest
from unittest.mock import (
    MagicMock,
    patch
)

import polling2
from requests.models import Response

from compliance_suite.exceptions.compliance_exception import (
    TestFailureException,
    TestRunnerException
)
from compliance_suite.functions.client import Client
from compliance_suite.functions.log import set_logging
from compliance_suite.functions.report import Report


class TestFunctions(unittest.TestCase):

    def setUp(self) -> None:
        """ Setup client object """
        self.client = Client(service="TES", server="test-server", version="1.0.0")

    def test_set_logging(self):
        """ Checks if the logger is set up properly """

        set_logging()
        assert True

    def test_report_generate(self):
        """Assert generate report method to be successful"""

        report = Report()
        report.report = MagicMock()
        report.generate()
        assert True

    @patch('requests.get')
    def test_send_request_get(self, mock_get):
        """ Asserts the Get endpoint response status to be 200"""

        mock_get.return_value = MagicMock(status_code=200)
        self.client.set_endpoint_data(endpoint="test-endpoint", uri_params={"test": "test"},
                                      query_params={"test": "test"}, operation="GET", request_body="")

        get_response = self.client.send_request()
        assert get_response.status_code == 200

    def test_send_request_get_failure(self):
        """ Asserts the Get endpoint to throw Connection error due to invalid server URL"""

        self.client.set_endpoint_data(endpoint="test-endpoint", uri_params={}, query_params={},
                                      operation="GET", request_body="")
        with self.assertRaises(TestRunnerException):
            self.client.send_request()

    @patch('requests.post')
    def test_send_request_post(self, mock_post):
        """ Asserts the Post endpoint response status to be 200"""

        mock_post.return_value = MagicMock(status_code=200)

        self.client.set_endpoint_data(endpoint="test-endpoint", uri_params={}, query_params={},
                                      operation="POST", request_body="{}")
        response = self.client.send_request()
        assert response.status_code == 200

    @patch('polling2.poll')
    def test_polling_request_success(self, mock_get):
        """ Asserts the polling response status to be 200"""

        mock_get.return_value = MagicMock(status_code=200)

        self.client.set_endpoint_data(endpoint="test-endpoint", uri_params={"test": "test"},
                                      query_params={"test": "test"}, operation="test", request_body="")
        get_response = self.client.poll_request(polling_interval=10, polling_timeout=3600, check_cancel_val=False)
        assert get_response.status_code == 200

    @patch('polling2.poll')
    def test_polling_request_timeout(self, mock_get):
        """ Asserts the polling request to throw Timeout Exception"""

        mock_get.side_effect = polling2.TimeoutException(MagicMock())

        self.client.set_endpoint_data(endpoint="test-endpoint", uri_params={"test": "test"},
                                      query_params={"test": "test"}, operation="test", request_body="")
        with self.assertRaises(TestFailureException):
            self.client.poll_request(polling_interval=10, polling_timeout=5, check_cancel_val=False)

    def test_polling_request_failure(self):
        """ Asserts the polling request to throw Timeout Exception"""

        self.client.set_endpoint_data(endpoint="test-endpoint", uri_params={"test": "test"},
                                      query_params={"test": "test"}, operation="test", request_body="")
        with self.assertRaises(TestRunnerException):
            self.client.poll_request(polling_interval=10, polling_timeout=3600, check_cancel_val=False)

    def test_check_poll_create(self):
        """ Asserts the check poll function to be True for status code 200 and COMPLETE state"""

        resp = MagicMock(status_code=200)
        resp.json.return_value = {"state": "COMPLETE"}

        assert self.client.check_poll(resp) is True

    def test_check_poll_cancel(self):
        """ Asserts the check poll function to be True for status code 200 and CANCELED state"""

        self.client.check_cancel = True
        resp = MagicMock(status_code=200)
        resp.json.return_value = {"state": "CANCELED"}

        assert self.client.check_poll(resp) is True

    def test_check_poll_fail(self):
        """ Asserts the check poll function to be False for status code not equal to 200"""

        resp = Response
        resp.status_code = 400

        assert self.client.check_poll(resp) is False

    def test_check_poll_retry(self):
        """ Asserts the check poll function to be False and retry for status code 200 and RANDOM state"""

        resp = MagicMock(status_code=200)
        resp.json.return_value = {"state": "RANDOM"}

        assert self.client.check_poll(resp) is False
