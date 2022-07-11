import os
import yaml
from test_runner import TestRunner

class JobRunner():

    def validate_job(self, yaml_data):
    # TODO - Validate if each required field present in YAML file
        pass

    def run_jobs(self):
        yaml_path = os.path.join(os.getcwd(), "compliance_suite", "jobs")
        for yaml_file in os.listdir(yaml_path):
            if yaml_file.endswith(".yml"):
                with open(os.path.join(yaml_path, yaml_file), "r") as f:
                    try:
                        yaml_data = yaml.safe_load(f)
                        # print(yaml_data)
                        self.validate_job(yaml_data)

                        auxiliary_space = {}
                        test_runner = TestRunner(yaml_data["server"], yaml_data["version"][0])
                        for job in yaml_data["jobs"]:
                            test_runner.run_tests(job, auxiliary_space)


                    except yaml.YAMLError as err:
                        print(f"Invalid YAML File - {yaml_file}")