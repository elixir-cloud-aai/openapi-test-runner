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
        client = Client()

        get_response = client.send_request(service="TES", server="test-server", version="test-version",
                                           endpoint="test-endpoint", uri_params={"test": "test"},
                                           query_params={"test": "test"}, operation="GET", request_body="")
        assert get_response.status_code == 200

    def test_send_request_get_failure(self):
        """ Asserts the Get endpoint to throw Connection error due to invalid server URL"""

        client = Client()
        with self.assertRaises(TestRunnerException):
            client.send_request(service="TES", server="test-server", version="test-version",
                                endpoint="test-endpoint", uri_params={}, query_params={},
                                operation="GET", request_body="")

    @patch('requests.post')
    def test_send_request_post(self, mock_post):
        """ Asserts the Post endpoint response status to be 200"""

        mock_post.return_value = MagicMock(status_code=200)

        client = Client()
        response = client.send_request(service="TES", server="test-server", version="test-version",
                                       endpoint="test-endpoint", uri_params={}, query_params={},
                                       operation="POST", request_body="{}")
        assert response.status_code == 200

    @patch('polling2.poll')
    def test_polling_request_success(self, mock_get):
        """ Asserts the polling response status to be 200"""

        mock_get.return_value = MagicMock(status_code=200)

        client = Client()
        get_response = client.poll_request(service="TES", server="test-server", version="test-version",
                                           endpoint="test-endpoint", uri_params={"test": "test"},
                                           query_params={"test": "test"}, operation="test",
                                           polling_interval=10, polling_timeout=3600,
                                           check_cancel_val=False)
        assert get_response.status_code == 200

    @patch('polling2.poll')
    def test_polling_request_timeout(self, mock_get):
        """ Asserts the polling request to throw Timeout Exception"""

        mock_get.side_effect = polling2.TimeoutException(MagicMock())

        client = Client()
        with self.assertRaises(TestFailureException):
            client.poll_request(service="TES", server="test-server", version="test-version",
                                endpoint="test-endpoint", uri_params={"test": "test"}, query_params={"test": "test"},
                                operation="test", polling_interval=10, polling_timeout=5, check_cancel_val=False)

    def test_polling_request_failure(self):
        """ Asserts the polling request to throw Timeout Exception"""

        client = Client()
        with self.assertRaises(TestRunnerException):
            client.poll_request(service="TES", server="invalid-url", version="test-version",
                                endpoint="test-endpoint", uri_params={"test": "test"}, query_params={"test": "test"},
                                operation="test", polling_interval=10, polling_timeout=3600, check_cancel_val=False)

    def test_check_poll_create(self):
        """ Asserts the check poll function to be True for status code 200 and COMPLETE state"""

        client = Client()
        resp = MagicMock(status_code=200)
        resp.json.return_value = {"state": "COMPLETE"}

        assert client.check_poll(resp) is True

    def test_check_poll_cancel(self):
        """ Asserts the check poll function to be True for status code 200 and CANCELED state"""

        client = Client()
        client.check_cancel = True
        resp = MagicMock(status_code=200)
        resp.json.return_value = {"state": "CANCELED"}

        assert client.check_poll(resp) is True

    def test_check_poll_fail(self):
        """ Asserts the check poll function to be False for status code not equal to 200"""

        client = Client()
        resp = Response
        resp.status_code = 400

        assert client.check_poll(resp) is False

    def test_check_poll_retry(self):
        """ Asserts the check poll function to be False and retry for status code 200 and RANDOM state"""

        client = Client()
        resp = MagicMock(status_code=200)
        resp.json.return_value = {"state": "RANDOM"}

        assert client.check_poll(resp) is False
