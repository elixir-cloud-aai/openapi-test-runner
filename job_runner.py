import os
import yaml
from test_runner import TestRunner

class JobRunner():

    def validate_job(self, yaml_data):
    # TODO - Validate if each required field present in YAML file
        pass

    def run_jobs(self):

        test_count = 0
        yaml_path = os.path.join(os.getcwd(), "compliance_suite", "jobs")
        for yaml_file in os.listdir(yaml_path):
            if yaml_file.endswith(".yml"):
                test_count += 1
                with open(os.path.join(yaml_path, yaml_file), "r") as f:
                    print(f"################################\nInitiating Test-{test_count} for {yaml_file}")
                    try:
                        yaml_data = yaml.safe_load(f)
                        # print(yaml_data)
                        self.validate_job(yaml_data)

                        test_runner = TestRunner(yaml_data["server"], yaml_data["version"][0])
                        job_count = 0
                        for job in yaml_data["jobs"]:
                            job_count += 1
                            print(f'Running tests for sub-job-{job_count} -> {job["name"]}')
                            test_runner.run_tests(job)

                    except yaml.YAMLError as err:
                        print(f"Invalid YAML File - {yaml_file}")
