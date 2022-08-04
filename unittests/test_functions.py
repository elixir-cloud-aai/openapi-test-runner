import unittest
from compliance_suite.functions.colored_console import print_blue, print_red, print_green, print_yellow, print_underline
from compliance_suite.functions.requestor import send_request, poll_request
import os
import yaml
from test_runner import TestRunner
from compliance_suite.exceptions.ComplianceException import ComplianceException

YAML_CREATE_TASK_REQUEST_SUCCESS = os.path.join(os.getcwd(), "unittests", "data", "tests", "success_create_task.yml")


class TestFunctions(unittest.TestCase):

    def test_colored_print(self):
        print_blue("Test blue")
        print_red("Test blue")
        print_green("Test blue")
        print_yellow("Test blue")
        print_underline("Test blue")
        assert True

    def test_send_request_get(self):
        # Create a task before get task
        with open(YAML_CREATE_TASK_REQUEST_SUCCESS) as f:
            yaml_data = yaml.safe_load(f)

        test_runner = TestRunner(yaml_data["server"], yaml_data["version"][0])
        test_runner.job_data = yaml_data["jobs"][0]

        post_response = send_request(test_runner.server, test_runner.version, test_runner.job_data["endpoint"],
                                    None, {}, test_runner.job_data["operation"], test_runner.job_data["request_body"])
        task_id = post_response.json()["id"]

        # Now, get task
        get_response = send_request(test_runner.server, test_runner.version, "/tasks/{id}",
                                    task_id, {"view": "MINIMAL"}, "GET", None)
        assert get_response.status_code == 200

    def test_send_request_post(self):
        with open(YAML_CREATE_TASK_REQUEST_SUCCESS) as f:
            yaml_data = yaml.safe_load(f)

        test_runner = TestRunner(yaml_data["server"], yaml_data["version"][0])
        test_runner.job_data = yaml_data["jobs"][0]

        response = send_request(test_runner.server, test_runner.version, test_runner.job_data["endpoint"],
                                None, {}, test_runner.job_data["operation"], test_runner.job_data["request_body"])
        assert response.status_code == 200

    def test_polling_request_success(self):
        # Create a task before get task
        with open(YAML_CREATE_TASK_REQUEST_SUCCESS) as f:
            yaml_data = yaml.safe_load(f)

        test_runner = TestRunner(yaml_data["server"], yaml_data["version"][0])
        test_runner.job_data = yaml_data["jobs"][0]

        post_response = send_request(test_runner.server, test_runner.version, test_runner.job_data["endpoint"],
                                     None, {}, test_runner.job_data["operation"], test_runner.job_data["request_body"])
        task_id = post_response.json()["id"]

        # Now, get task
        get_response = poll_request(test_runner.server, test_runner.version, "/tasks/{id}",
                                    task_id, {"view": "MINIMAL"}, "GET", 10, 3600, False)
        assert get_response.status_code == 200

    def test_polling_request_timeout(self):
        # Create a task before get task
        with open(YAML_CREATE_TASK_REQUEST_SUCCESS) as f:
            yaml_data = yaml.safe_load(f)

        test_runner = TestRunner(yaml_data["server"], yaml_data["version"][0])
        test_runner.job_data = yaml_data["jobs"][0]

        post_response = send_request(test_runner.server, test_runner.version, test_runner.job_data["endpoint"],
                                     None, {}, test_runner.job_data["operation"], test_runner.job_data["request_body"])
        task_id = post_response.json()["id"]

        with self.assertRaises(ComplianceException):
            get_response = poll_request(test_runner.server, test_runner.version, "/tasks/{id}",
                                        task_id, {"view": "MINIMAL"}, "GET", 10, 5, False)
