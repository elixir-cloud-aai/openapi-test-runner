import os
from jsonschema import validate, SchemaError, ValidationError
import yaml
from test_runner import TestRunner
from compliance_suite.exceptions.ComplianceException import ComplianceException
from compliance_suite.functions.colored_console import print_blue, print_red, print_green, print_yellow


class JobRunner():

    def __init__(self, tags):
        self.path = os.getcwd()
        self.tags = tags
        self.test_count = 0
        self.result = {
            "passed": 0,
            "failed": 0,
            "skipped": 0
        }
        self.test_status = {
            "passed": [],
            "failed": [],
            "skipped": []
        }

    def generate_summary(self):

        passed_tests = ", ".join(self.test_status["passed"])
        failed_tests = ", ".join(self.test_status["failed"])
        skipped_tests = ", ".join(self.test_status["skipped"])

        print("\n\n\n")
        print_yellow("{:#^90}".format("   Compliance Testing Summary   "))
        print_yellow("#{:^88}#".format(""))
        print_yellow("#{:^88}#".format(f"Total Tests - {self.test_count}"))
        print_yellow("#{:^88}#".format(f'Passed - {self.result["passed"]} ({passed_tests})'))
        print_yellow("#{:^88}#".format(f'Failed - {self.result["failed"]} ({failed_tests})'))
        print_yellow("#{:^88}#".format(f'Skipped - {self.result["skipped"]} ({skipped_tests})'))
        print_yellow("#{:^88}#".format(""))
        print_yellow("{:#^90}".format(""))

    def validate_job(self, yaml_data, yaml_file):
        schema_path = os.path.join(self.path, "tests", "template", "test_template_schema.json")
        with open(schema_path, "r") as f:
            json_schema = yaml.safe_load(f)

        try:
            validate(yaml_data, json_schema)
            print(f'Test YAML file valid for {yaml_file}')
        except ValidationError as err:
            raise ComplianceException(f"YAML schema validation error - {yaml_file}. Error details - {err.message}")

    def run_jobs(self):

        yaml_path = os.path.join(self.path, "tests")
        for yaml_file in os.listdir(yaml_path):
            if yaml_file.endswith(".yml"):
                self.test_count += 1
                with open(os.path.join(yaml_path, yaml_file), "r") as f:
                    print("\n{:#^100}".format(f"     Initiating Test-{self.test_count} for {yaml_file}     "))
                    try:
                        try:
                            yaml_data = yaml.safe_load(f)
                        except yaml.YAMLError as err:
                            raise ComplianceException(f"Invalid YAML File - {yaml_file}. Error details - {err}")
                        # print(yaml_data)
                        self.validate_job(yaml_data, yaml_file)

                        tag_matched = False
                        # print(f' {self.tags}   {yaml_data["tags"]}')
                        for tag in self.tags:
                            if tag in yaml_data["tags"]:
                                tag_matched = True
                                test_runner = TestRunner(yaml_data["server"], yaml_data["version"][0])
                                job_count = 0
                                for job in yaml_data["jobs"]:
                                    job_count += 1
                                    print(f'Running tests for sub-job-{job_count} -> {job["name"]}')
                                    test_runner.run_tests(job)
                                self.result["passed"] += 1
                                self.test_status["passed"].append(str(self.test_count))
                                print_green(f'Compliance Test-{self.test_count} for {yaml_file} successful.')
                        if not tag_matched:
                            self.result["skipped"] += 1
                            self.test_status["skipped"].append(str(self.test_count))
                            print_blue(f"No Tag matched. Skipping Test-{self.test_count} for {yaml_file}")

                    except ComplianceException as err:
                        self.result["failed"] += 1
                        self.test_status["failed"].append(str(self.test_count))
                        print_red(f'Compliance Test-{self.test_count} for {yaml_file} failed.')
                        print_red(f'Error - {err}')

        self.generate_summary()
