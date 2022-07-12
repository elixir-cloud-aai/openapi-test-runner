from pydantic import ValidationError
from compliance_suite.functions.requestor import send_request
from compliance_suite.constants.constants import VERSION_INFO, ENDPOINT_TO_MODEL
from compliance_suite.models.v1_0_specs import *

class TestRunner():

    def __init__(self, server, version):

        self.server = server
        self.version = VERSION_INFO[version]
        self.job_data = None

    def validate_response(self, response):

        # General status validation
        response_status = list(self.job_data["response"].keys())[0]
        if response.status_code == response_status:
            print(f"Successful request")
        else:
            print("Request Failed. Incorrect Response Status Code.")

        # Logical Schema Validation

        response_json = response.json()
        # print(response_json)

        try:
            endpoint_model = None
            if self.job_data["name"] in ["list_tasks", "get_task"]:
                view_query = [item["view"] for item in self.job_data["query_parameters"]]
                endpoint_model = self.job_data["name"] + "_" + view_query[0]
            else:
                endpoint_model = self.job_data["name"]

            ENDPOINT_TO_MODEL[endpoint_model](**response_json)
            print(f'Schema validation successful for {self.job_data["endpoint"]}')
        except ValidationError as err:
            print(err)


    def run_tests(self, job_data, auxiliary_space):

        # print(job_data)
        self.job_data = job_data
        response = send_request(self.server, self.version, job_data["endpoint"], job_data["operation"])
        self.validate_response(response)

