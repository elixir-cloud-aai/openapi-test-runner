## Tests - Deep Analysis 

Once the test flow is decided, the YAML test file can be created containing the relevant information. 
To understand how this works inside the compliance suite, a deep analysis is provided.

## Step 1 - Create a YAML test file
As shown in the previous sections, the YAML file consist of multiple endpoint modules to enable real world 
scenario replication. The YAML file schema and template (present in codebase) can be referred to create it.

## Step 2 - Run the compliance suite
Now, the user can run the compliance suite for specific tags. If the user-provided tags match the YAML test 
tags, the test will be executed.

## Step 3 - YAML checks
To ensure the YAML file is valid and information can be parsed from it, two checks are implemented.

1. YAML validation - This checks if the file is in proper YAML format and parseable.
2. YAML schema validation - This compares the YAML file against the pre-define schema. It ensures that the 
3. necessary fields like server details, endpoint details, etc are present.

## Step 4 - Individual job checks
The job info is parsed from the YAML file and sent forward to execute it. It will send request to the server 
and return a response while storing necessary details in the auxiliary space.

The following checks are implemented on it.

 - If job contains a request body -
     1. JSON validation - This checks if the request body is in proper JSON format and parseable
     2. Request body schema validation - The request body is compared against the model to verify its conformance.

 - The response validation includes - 
     1. Status validation - The response HTTP status is validated against the HTTP status defined in the YAML test file
     2. Logical response validation - The response body is compared against the model to verify its conformance.
     3. Functional response validation - The response is validated to assess the TES server functionality. 
        It verifies that the cloud features such as S3 storage work as intended. (This feature is in works and will be completed soon)

 - Polling validations - 
While monitoring the task status in case of Create/Cancel task, the request is polled at the user-provided interval
     1. Task status validation - It verifies that the returned task status is appropriate depending on whether its Create/Cancel task.
     2. Timeout - If the polling timeout limit is exceeded, a Timeout Exception is thrown.

 - Filter validations (Optional) - 
The suite offers an API data validation based on specific API data path and filter value. If no filtered data is found,
then `TestFailureException` is thrown.


## Step 5 - Summary and Report Generation

After all the YAML tests are completed, the results are compiled. A summary is displayed over the console giving info
about the test status and corresponding tests.

![Summary](/docs/images/summary.JPG)

A JSON report is published at the end according to the `ga4gh-testbed-lib` standards. It contains the phases, tests and cases details.

![Json_Report](/docs/images/json_report.JPG)