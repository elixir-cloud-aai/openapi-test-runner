"""Module unittests.test_functions.py

This module is to test the project functions
"""

import os
import unittest

import yaml

from compliance_suite.exceptions.compliance_exception import (
    TestFailureException,
    TestRunnerException
)
from compliance_suite.functions.client import Client
from compliance_suite.functions.log import set_logging
from compliance_suite.test_runner import TestRunner

YAML_CREATE_TASK_REQUEST_SUCCESS = os.path.join(os.getcwd(), "unittests", "data", "tests", "success_create_task.yml")
YAML_SERVICE_INFO_FAIL = os.path.join(os.getcwd(), "unittests", "data", "tests", "fail_service_info.yml")


class TestFunctions(unittest.TestCase):

    def test_set_logging(self):
        """ Checks if the logger is set up properly """

        set_logging()
        assert True

    def test_send_request_get(self):
        """ Asserts the Get endpoint response status to be 200"""

        # Create a task before get task
        with open(YAML_CREATE_TASK_REQUEST_SUCCESS) as f:
            yaml_data = yaml.safe_load(f)

        test_runner = TestRunner(yaml_data["service"], yaml_data["server"], yaml_data["version"][0])
        test_runner.set_job_data(yaml_data["jobs"][0])
        client = Client()

        post_response = client.send_request(service=test_runner.service, server=test_runner.server,
                                            version=test_runner.version, endpoint=test_runner.job_data["endpoint"],
                                            uri_params={}, query_params={},
                                            operation=test_runner.job_data["operation"],
                                            request_body=test_runner.job_data["request_body"])
        task_id = post_response.json()["id"]

        # Now, get task
        get_response = client.send_request(service=test_runner.service, server=test_runner.server,
                                           version=test_runner.version, endpoint="/tasks/{id}",
                                           uri_params={"id": task_id}, query_params={"view": "MINIMAL"},
                                           operation="GET", request_body="{}")
        assert get_response.status_code == 200

    def test_send_request_get_failure(self):
        """ Asserts the Get endpoint to throw Connection error due to invalid server URL"""

        # Create a task before get task
        with open(YAML_SERVICE_INFO_FAIL) as f:
            yaml_data = yaml.safe_load(f)

        test_runner = TestRunner(yaml_data["service"], yaml_data["server"], yaml_data["version"][0])
        test_runner.set_job_data(yaml_data["jobs"][0])
        client = Client()

        with self.assertRaises(TestRunnerException):
            client.send_request(service=test_runner.service, server=test_runner.server,
                                version=test_runner.version, endpoint="/service-info",
                                uri_params={}, query_params={},
                                operation="GET", request_body="{}")

    def test_send_request_post(self):
        """ Asserts the Post endpoint response status to be 200"""

        with open(YAML_CREATE_TASK_REQUEST_SUCCESS) as f:
            yaml_data = yaml.safe_load(f)

        test_runner = TestRunner(yaml_data["service"], yaml_data["server"], yaml_data["version"][0])
        test_runner.set_job_data(yaml_data["jobs"][0])
        client = Client()

        response = client.send_request(service=test_runner.service, server=test_runner.server,
                                       version=test_runner.version, endpoint=test_runner.job_data["endpoint"],
                                       uri_params={}, query_params={}, operation=test_runner.job_data["operation"],
                                       request_body=test_runner.job_data["request_body"])
        assert response.status_code == 200

    def test_polling_request_success(self):
        """ Asserts the polling response status to be 200"""

        # Create a task before get task
        with open(YAML_CREATE_TASK_REQUEST_SUCCESS) as f:
            yaml_data = yaml.safe_load(f)

        test_runner = TestRunner(yaml_data["service"], yaml_data["server"], yaml_data["version"][0])
        test_runner.set_job_data(yaml_data["jobs"][0])
        client = Client()

        post_response = client.send_request(service=test_runner.service, server=test_runner.server,
                                            version=test_runner.version, endpoint=test_runner.job_data["endpoint"],
                                            uri_params={}, query_params={},
                                            operation=test_runner.job_data["operation"],
                                            request_body=test_runner.job_data["request_body"])
        task_id = post_response.json()["id"]

        # Now, get task
        get_response = client.poll_request(service=test_runner.service, server=test_runner.server,
                                           version=test_runner.version, endpoint="/tasks/{id}",
                                           uri_params={"id": task_id}, query_params={"view": "MINIMAL"},
                                           operation="GET", polling_interval=10, polling_timeout=3600,
                                           check_cancel_val=False)
        assert get_response.status_code == 200

    def test_polling_request_timeout(self):
        """ Asserts the polling request to throw Timeout Exception"""

        # Create a task before get task
        with open(YAML_CREATE_TASK_REQUEST_SUCCESS) as f:
            yaml_data = yaml.safe_load(f)

        test_runner = TestRunner(yaml_data["service"], yaml_data["server"], yaml_data["version"][0])
        test_runner.set_job_data(yaml_data["jobs"][0])
        client = Client()

        post_response = client.send_request(service=test_runner.service, server=test_runner.server,
                                            version=test_runner.version, endpoint=test_runner.job_data["endpoint"],
                                            uri_params={}, query_params={},
                                            operation=test_runner.job_data["operation"],
                                            request_body=test_runner.job_data["request_body"])
        task_id = post_response.json()["id"]

        with self.assertRaises(TestFailureException):
            client.poll_request(service=test_runner.service, server=test_runner.server, version=test_runner.version,
                                endpoint="/tasks/{id}", uri_params={"id": task_id}, query_params={"view": "MINIMAL"},
                                operation="GET", polling_interval=10, polling_timeout=5, check_cancel_val=False)
