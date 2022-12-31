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

## Usage

The following command line parameters can be run:

| Parameter     | Short Name | Required |Description |
|---------------|------------|----------|---|
| --tag         | -t         | No       |  Tag for which the compliance suite will be run. It is case insensitive. Default - all |
| --output_path | -o         | No       |The output path to store the JSON compliance report |
| --serve       | NA         | No       |If set, runs a local server and displays the JSON report in HTML web page |
| --port        | NA         | No       | The port at which the local server is run. Default - 15800 |
| --uptime      | -u         | No       |The local server duration in seconds. Default - 3600 seconds |

Multiple tags can be set by providing multiple `--tag` or `-t` parameter.
```base  
tes-compliance-suite report --tag "cancel task" --tag "create task" --tag "get task"  
```  

## Notes

1. Some examples for command line are:
```base  
tes-compliance-suite report --tag "all" 
tes-compliance-suite report --tag "all" --output_path "path/to/store" --serve --port 9090 --uptime 1000
``` 

2.  If the HOME python version is different than 3.8, then absolute path with reference to 3.8 should be used.
```base  
path/to/python3.8/python setup.py install
path/to/python3.8/Scripts/tes-compliance-suite report
```