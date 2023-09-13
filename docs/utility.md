# Getting Started  

The TES compliance suite tests the server conformance to the TES API specifications. 
The tool can be installed and executed from the command line. 
The YAML test files can be modified to run the compliance tests for user-defined configuration.

The compliance suite generates a report, giving the summary and detailed view of the tests. 
The report can also be viewed as HTML web page in local server.

## Installation  

Python 3.8 is the supported Python version and should be installed as a pre-requisite.
The following steps will guide you to install the suite.

1.  Clone the latest codebase from [https://github.com/elixir-cloud-aai/openapi-test-runner](https://github.com/elixir-cloud-aai/openapi-test-runner)

```base  
git clone https://github.com/elixir-cloud-aai/openapi-test-runner.git  
```
  2.  Enter openapi-test-runner directory and install
  
```base  
cd openapi-test-runner
python setup.py install  
```  
3.  Confirm installation by executing the openapi-test-runner command

```base  
openapi-test-runner report --help
```
  
## YAML Test files

Verify or modify the YAML test files according to the requirements.
The YAML files are present at the `/tests` directory. 
The template and JSON schema can be found at `/tests/template`.

The package needs to be updated everytime the files are updated, run the setup command again.
```base  
python setup.py install  
``` 

### Test file features

The test files provide multiple features for better operability and extensibility. 

1. Storage Variables - Persist response values to be used in subsequent jobs. When using a storage variable, it should
   be enclosed in curly brackets and quotes to denote its usage. Refer the [test syntax][res-test-syntax] for syntax details. 
   Example - "$response.id" is extracted from the CreateTask response and stored in the key "id" for later
   GetTask or CancelTask jobs.

    ```base
    storage_vars:
      id: $response.id
    key: "{id}"
    ```

2. Environment Variables - Define key-value pairs to be referenced inside the code.
   Refer the [test syntax][res-test-syntax] for syntax details.
   Example - 

    ```base
    env_vars:
      check_cancel: True
    ```

3. Path Parameters - Define multiple endpoint path parameters values by using either storage variables or exact values.
   Refer the [test syntax][res-test-syntax] for syntax details.
   Example -

    ```base
    path_parameters:
      foo: 1234
      lorem: "{ipsum}"
    ```

4. Templates - Templates help eliminate the redundancy of creating the same tasks in multiple test files. 
   A template consists of a list of jobs and undergoes validation against a schema check.
   Additionally, templates can store variables that receive values from argument key-value pairs in the test file.
   To use a stored variable, enclose it in curly brackets and quotes to indicate its usage.
   Refer the [test syntax][res-test-syntax] for syntax details. 

   <br>
   
   Few points to note:
      1. Use unique names for variables.
      2. The existing `storage_vars` and `parameters` will not be affected and continue to work as they are.

   <br>
   Example - 

 - Template file
    ```base 
    - name: template_name
      query_parameters:
        id: "{id_value}"
    ```
   
 - Test file 1
    ```base
    jobs:
      - $ref: "path/to/template"
        args:
          id_value: "123"
    ```
   
 - Test file 2
    ```base
    jobs:
      - $ref: "path/to/template"
        args:
          id_value: "789"
    ```

## Usage

The following command line parameters can be run:

| Parameter      | Short Name | Required | Multiple? | Description                                                                                           |
|----------------|------------|----------|-----------|-------------------------------------------------------------------------------------------------------|
| --server       | -s         | Yes      | No        | The server URL on which the compliance suite will be run. Format - `https://<url>/`                   |
| --version      | -v         | Yes      | No        | The compliance suite will be run against this TES version. Format - SemVer. Example - `"1.0.0"`       |
| --include-tags | -i         | No       | Yes       | Tag for which the compliance suite will be run. It is case insensitive.                               |
| --exclude-tags | -e         | No       | Yes       | Tag for which the compliance suite will be skipped. It is case insensitive.                           |
| --test-path    | -tp        | No       | Yes       | The absolute or relative path from the project root of the test file/directory. Default - `["tests"]` |
| --output_path  | -o         | No       | No        | The output path to store the JSON compliance report                                                   |
| --serve        | N/A        | No       | N/A       | If set, runs a local server and displays the JSON report in HTML web page                             |
| --port         | N/A        | No       | N/A       | The port at which the local server is run. Default - 15800                                            |
| --uptime       | -u         | No       | No        | The local server duration in seconds. Default - 3600 seconds                                          |

### Tags

- Only letters (a-z, A-Z), digits (0-9) and underscores (_) are allowed.

- Multiple tags can be set by providing multiple `--include-tags` or `--exclude-tags` parameter.
  ```base  
  openapi-test-runner report --server "https://test.com/" --include-tags tag_1 --include-tags TAG2 --include-tags 123  
  ```  

- A test is run if none of the `--exclude-tags` match any of the Yaml test tags, and at least one of the `--include-tags` is present in the Yaml test tags. Example -  
  <br>
  If `--include-tags` = `["tag1", "tag2"]` and `--exclude-tags` = `["tag3"]`, then   
  `Test1.yaml` with tags = `["tag1", "tag4"]` will run  
  `Test2.yaml` with tags = `["tag2", "tag3"]` will not run

- If `--include-tags` is not specified, all tests are assumed to be included by default and will be executed.

## Notes

1. Some examples for command line are:
```base  
openapi-test-runner report --server "https://test.com/" --version "1.0.0"
openapi-test-runner report --server "https://test.com/" --version "1.0.0" --include-tags "schema_validation_only" --test-path "path/to/test" --output_path "path/to/store" --serve --port 9090 --uptime 1000
``` 

2.  If the HOME python version is different from 3.8, then absolute path with reference to 3.8 should be used.
```base  
path/to/python3.8/python setup.py install
path/to/python3.8/Scripts/openapi-test-runner report
```

## Docker image

The project has a [Dockerfile][dockerfile] that creates an ubuntu based container image ready to run openapi-test-runner. It uses [entrypoint.sh][entrypoint] as an entrypoint, which is most useful if the url of the server changes each time the test suite is run or if only specific tests need to be run. Also, if the server requires basic authentication to connect to, entrypoint.sh can be edited to accept not just the endpoint url, but the username and password as well. 

```base  
http://$tesuser:$tespassword@$teshostname/
```

Currently, the TES endpoint url in entrypoint.sh will grab the value from an environmental variable in the image. However, entrypoint.sh gives flexibility to define how that value can be populated. For example, a file can be copied over to the image containing the endpoint url, username and password which could then be read and parsed to pass into tes-compliance suite. Refer to the example below. 

```base  
#!/bin/sh
teshostname=$(jq -r '.TesHostname' TesCredentials.json)
tesuser=$(jq -r '.TesUsername' TesCredentials.json)
tespassword=$(jq -r '.TesPassword' TesCredentials.json)

openapi-test-runner report --server http://$tesuser:$tespassword@$teshostname/ --include-tags all --output_path results
```

[res-test-syntax]: test_config/test_syntax.yml
[dockerfile]: ../docker/Dockerfile
[entrypoint]: ../docker/entrypoint.sh