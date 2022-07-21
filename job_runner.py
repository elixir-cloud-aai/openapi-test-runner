import os
from jsonschema import validate, SchemaError, ValidationError
import yaml
from test_runner import TestRunner


class JobRunner():

    def __init__(self, tags):
        self.path = os.getcwd()
        self.tags = tags


    def validate_job(self, yaml_data):
        schema_path = os.path.join(self.path, "tests", "template", "test_template_schema.json")
        with open(schema_path, "r") as f:
            json_schema = yaml.safe_load(f)

        try:
            validate(yaml_data, json_schema)
            print(f'Test YAML file valid for {yaml_data["name"]}')
        except (SchemaError, ValidationError) as err:
            print(f"Error is {err}")

    def run_jobs(self):

        test_count = 0
        yaml_path = os.path.join(self.path, "tests")
        for yaml_file in os.listdir(yaml_path):
            if yaml_file.endswith(".yml"):
                test_count += 1
                with open(os.path.join(yaml_path, yaml_file), "r") as f:
                    print(f"################################\nInitiating Test-{test_count} for {yaml_file}")
                    try:
                        yaml_data = yaml.safe_load(f)
                        # print(yaml_data)
                        self.validate_job(yaml_data)

                        tag_matched = False
                        print(f' {self.tags}   {yaml_data["tags"]}')
                        for tag in self.tags:
                            if tag in yaml_data["tags"]:
                                tag_matched = True
                                test_runner = TestRunner(yaml_data["server"], yaml_data["version"][0])
                                job_count = 0
                                for job in yaml_data["jobs"]:
                                    job_count += 1
                                    print(f'Running tests for sub-job-{job_count} -> {job["name"]}')
                                    test_runner.run_tests(job)
                        if not tag_matched:
                            print(f"No Tag matched. Skipping Test-{test_count} for {yaml_file}")

                    except yaml.YAMLError as err:
                        print(f"Invalid YAML File - {yaml_file}. Error details - {err}")
