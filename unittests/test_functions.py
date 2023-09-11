"""Module unittests.test_functions.py

This module is to test the project functions
"""

from unittest.mock import (
    MagicMock,
    patch
)

import polling2
import pytest
from requests.models import Response

from compliance_suite.exceptions.compliance_exception import (
    TestFailureException,
    TestRunnerException
)
from compliance_suite.functions.client import Client
from compliance_suite.functions.report import Report


class TestFunctions:

    @pytest.fixture
    def client(self):
        """Pytest fixture for client"""

        with patch("importlib.import_module"):
            client = Client()
            yield client

    def test_report_generate(self):
        """Assert generate report method to be successful"""

        report = Report()
        report.report = MagicMock()
        report.generate()
        assert True

    @patch('requests.get')
    def test_send_request_get(self, mock_get, client):
        """ Asserts the Get endpoint response status to be 200"""

        mock_get.return_value = MagicMock(status_code=200)

        get_response = client.send_request(server="test-server", version="test-version",
                                           endpoint="test-endpoint", path_params={"test": "test"},
                                           query_params={"test": "test"}, operation="GET", request_body="")
        assert get_response.status_code == 200

    def test_send_request_get_failure(self, client):
        """ Asserts the Get endpoint to throw Connection error due to invalid server URL"""

        with pytest.raises(TestRunnerException):
            client.send_request(server="test-server", version="test-version",
                                endpoint="test-endpoint", path_params={}, query_params={},
                                operation="GET", request_body="")

    @patch('requests.post')
    def test_send_request_post(self, mock_post, client):
        """ Asserts the Post endpoint response status to be 200"""

        mock_post.return_value = MagicMock(status_code=200)

        response = client.send_request(server="test-server", version="test-version",
                                       endpoint="test-endpoint", path_params={}, query_params={},
                                       operation="POST", request_body="{}")
        assert response.status_code == 200

    @patch('polling2.poll')
    def test_polling_request_success(self, mock_get, client):
        """ Asserts the polling response status to be 200"""

        mock_get.return_value = MagicMock(status_code=200)

        get_response = client.poll_request(server="test-server", version="test-version",
                                           endpoint="test-endpoint", path_params={"test": "test"},
                                           query_params={"test": "test"}, operation="test",
                                           polling_interval=10, polling_timeout=3600,
                                           check_cancel_val=False)
        assert get_response.status_code == 200

    @patch('polling2.poll')
    def test_polling_request_timeout(self, mock_get, client):
        """ Asserts the polling request to throw Timeout Exception"""

        mock_get.side_effect = polling2.TimeoutException(MagicMock())

        with pytest.raises(TestFailureException):
            client.poll_request(server="test-server", version="test-version",
                                endpoint="test-endpoint", path_params={"test": "test"}, query_params={"test": "test"},
                                operation="test", polling_interval=10, polling_timeout=5, check_cancel_val=False)

    def test_polling_request_failure(self, client):
        """ Asserts the polling request to throw OSError"""

        with pytest.raises(TestRunnerException):
            client.poll_request(server="invalid-url", version="test-version",
                                endpoint="test-endpoint", path_params={"test": "test"}, query_params={"test": "test"},
                                operation="test", polling_interval=10, polling_timeout=3600, check_cancel_val=False)

    def test_check_poll_create(self, client):
        """ Asserts the check poll function to be True for status code 200 and COMPLETE state"""

        resp = MagicMock(status_code=200)
        resp.json.return_value = {"state": "COMPLETE"}

        assert client.check_poll(resp) is True

    def test_check_poll_cancel(self, client):
        """ Asserts the check poll function to be True for status code 200 and CANCELED state"""

        client.check_cancel = True
        resp = MagicMock(status_code=200)
        resp.json.return_value = {"state": "CANCELED"}

        assert client.check_poll(resp) is True

    def test_check_poll_canceling(self, client):
        """ Asserts the check poll function to be True for status code 200 and CANCELING state"""

        client.check_cancel = True
        resp = MagicMock(status_code=200)
        resp.json.return_value = {"state": "CANCELING"}

        assert client.check_poll(resp) is True

    def test_check_poll_fail(self, client):
        """ Asserts the check poll function to be False for status code not equal to 200"""

        resp = Response
        resp.status_code = 400

        assert client.check_poll(resp) is False

    def test_check_poll_retry(self, client):
        """ Asserts the check poll function to be False and retry for status code 200 and RANDOM state"""

        resp = MagicMock(status_code=200)
        resp.json.return_value = {"state": "RANDOM"}

        assert client.check_poll(resp) is False
