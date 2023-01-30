# Getting Started  

The TES compliance suite tests the server conformance to the TES API specifications. 
The tool can be installed and executed from the command line. 
The YAML test files can be modified to run the compliance tests for user-defined configuration.

The compliance suite generates a report, giving the summary and detailed view of the tests. 
The report can also be viewed as HTML web page in local server.

## Installation  

Python 3.8 is the supported Python version and should be installed as an pre-requisite.
The following steps will guide you to install the suite.

1.  Clone the latest codebase from  [https://github.com/elixir-cloud-aai/tes-compliance-suite](https://github.com/elixir-cloud-aai/tes-compliance-suite)

```base  
git clone https://github.com/elixir-cloud-aai/tes-compliance-suite.git  
```
  2.  Enter tes-compliance-suite directory and install
  
```base  
cd tes-compliance-suite  
python setup.py install  
```  
3.  Confirm installation by executing the tes-compliance-suite command

```base  
tes-compliance-suite report --help
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

1. Storage Variables - Persist response values to be used in subsequent jobs. 
   Refer the [test template][res-test-template] for syntax details.
   Example - "$response.id" is extracted from the CreateTask response and stored in the key "id" for later
   GetTask or CancelTask jobs.

```base
storage_vars:
      id: $response.id
```

2. Environment Variables - Define key-value pairs to be referenced inside the code.
   Refer the [test template][res-test-template] for syntax details.
   Example - 

```base
env_vars:
      check_cancel: True
```

## Usage

The following command line parameters can be run:

| Parameter     | Short Name | Required |Description |
|---------------|------------|----------|---|
| --server      | -s         | Yes      |The server URL on which the compliance suite will be run. Format - `https://<url>/`|
| --version     | -v         | No       |The compliance suite will be run against this TES version. Default - Latest version. Example - `"v1.0"`|
| --tag         | -t         | No       |Tag for which the compliance suite will be run. It is case insensitive. Default - `"all"` |
| --output_path | -o         | No       |The output path to store the JSON compliance report |
| --serve       | NA         | No       |If set, runs a local server and displays the JSON report in HTML web page |
| --port        | NA         | No       |The port at which the local server is run. Default - 15800 |
| --uptime      | -u         | No       |The local server duration in seconds. Default - 3600 seconds |

Multiple tags can be set by providing multiple `--tag` or `-t` parameter.
```base  
tes-compliance-suite report --server "https://test.com/" --tag "cancel task" --tag "create task" --tag "get task"  
```  

## Notes

1. Some examples for command line are:
```base  
tes-compliance-suite report --server "https://test.com/" --tag "all" 
tes-compliance-suite report --server "https://test.com/" --version "v1.0" --tag "all" --output_path "path/to/store" --serve --port 9090 --uptime 1000
``` 

2.  If the HOME python version is different than 3.8, then absolute path with reference to 3.8 should be used.
```base  
path/to/python3.8/python setup.py install
path/to/python3.8/Scripts/tes-compliance-suite report
```

## Docker image

The project has a [Dockerfile][dockerfile] that creates a ubuntu based container image ready to run tes-compliance-suite. It uses [entrypoint.sh][entrypoint] as an entrypoint, which is most useful if the url of the server changes each time the test suite is run or if only specific tests need to be run. Also, if the server requires basic authentication to connect to, entrypoint.sh can be edited to accept not just the endpoint url, but the username and password as well. 

```base  
http://$tesuser:$tespassword@$teshostname/
```

Currently the TES endpoint url in entrypoint.sh will grab the value from an enviormental variable in the image. However, entrypoint.sh gives flexibility to define how that value can be populated. For example, a file can be copied over to the image containing the endpoint url, username and password which could then be read and parsed to pass into tes-compliance suite. Refer to the example below. 

```base  
#!/bin/sh
teshostname=$(jq -r '.TesHostname' TesCredentials.json)
tesuser=$(jq -r '.TesUsername' TesCredentials.json)
tespassword=$(jq -r '.TesPassword' TesCredentials.json)

tes-compliance-suite report --server http://$tesuser:$tespassword@$teshostname/ --tag all --output_path results
```

[res-test-template]: ../tests/template/test_template.yml
[dockerfile]: ../docker/Dockerfile
[entrypoint]: ../docker/entrypoint.sh