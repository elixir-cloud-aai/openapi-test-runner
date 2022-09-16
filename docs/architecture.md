# Compliance Suite Architecture

The compliance suite is designed to be as modularized and automated as possible. 
We create individual YAML files to test TES endpoints and provide necessary details.
The components take care of executing the tests, validating and generating the reports.

The YAML files contain common fields related to Test details and server info. It contains multiple jobs which
represent combination of individual TES endpoints.
These individual jobs contain necessary info like `name`, `endpoint`, `operation`, etc.

The YAML test files are designed to flow sequentially without the need to be dependent on other test files. The flows should be intuitive.
The aim is not have a global storage of data which might result in difficulties in complex functional scenarios. 
This approach enables the Tests to be loosely coupled and not hard coded in the codebase.
Any number of job combinations and tests can be executed this way without needing to modify the codebase.

For example, File1 is supposed to test `ListTasks` endpoint and File2 is supposed to test `GetTask` endpoint. 
File1 will contain a sub-job to test `ListTasks` endpoint and it will be validated.
File2 will contain a combo of jobs. It will have a `ListTasks` sub-job and a `GetTask` sub-job. 
First, `ListTasks` will be executed (and validated) and then using this response, `GetTask` will be executed 
and validated. The `GetTask` is dependent on the `ListTasks` on File2, instead of File1 which would have required global storage of data.

The YAML Test file template and JSON schema is present at `/tests/template`

## Components

The compliance suite has 3 components - 
1. YAML Job Parser
2. Test Runner
3. Report Generator

![Architecture Diagram](/docs/images/Architecture.svg)

## YAML Job Parser

All the YAML files are present in the `/tests` directory.
The Runner scans all the YAML files and process them individually.

The functions are - 
1. Validate YAML file - The YAML files are validated to have a proper YAML format. Raises Exception if any error found.
2. Validate required fields - Each YAML job should have common mandatory fields like `server` and the sub jobs 
   should have mandatory fields like `name`, `endpoint`, `operation`, etc.
   The parser validates all the fields and raises exception if any error found
3. Parse the data and send to Test Runner to execute and validate the tests.

## Test Runner

The test runner contains the common details like `server` and individual job details sent from Job Parser.
The test runner contains a common auxiliary space which stores the result of all the jobs being run inside a **_single_** test.
For example, ListTasks will store its data in common auxiliary space which can be used by GetTask later.

The functions are - 
1. Validate request body - If its a POST request (i.e. CreateTask), the request body is validated for proper JSON 
   format and schema model validation. It raises Exception if any error found.
2. Send the request - A requestor function is called which sends the request with provided details like URL, 
   Endpoint, Request Body, etc. It returns the response.
3. Response Validation - The response validation can be broken into 3 steps based on its complexity.
   1. General validation - HTTP Response Status and Response Headers like `Accept` and `Content-Type` are checked here.
   2. Schema model validation - The response is validated against the appropriate `Pydantic` model class. It returns
      a list of errors if the validation fails.
   3. Functional validation - In YAML Test file, we provide the expected response body. Here, we match the expected 
      body with the actual response. It raises Exception if any error found. For example, we create a task with
      "Hello World" command. Now, we will GetTask and validate if the response contains "Hello World" command or not. 
      This can similarly be extended to tackle complex scenarios.

## Report Generator

A final report is generated which showcases all our test results. This report is also send to the central GA4GH 
Testbed which hosts similar compliance test reports.
        
The functions are - 
1. Generate report - A common GA4GH Testbed Python Library has been developed focusing on generating reports. 
   It will be used to generate the report.
2. Display HTML web view in local server - As part of CLI arguments, if local server is enabled, a web view 
   will be hosted on the local server which will display our report in HTML.
3. Push the report to GA4GH Testbed API - To send the report to central GA4GH Testbed, an API request is sent 
   containing relevant info (This feature is still in development at the GA4GH Testbed. It will be implemented
   in complaince suite once completed)
