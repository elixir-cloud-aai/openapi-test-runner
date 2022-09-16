
## Preamble  
Welcome to TES Compliance documentation.

This documentation describes the TES compliance suite to determine a server's compliance with the
[TES API specification](https://github.com/ga4gh/task-execution-schemas/blob/develop/openapi/task_execution_service.openapi.yaml).
The specification has been developed by the [Global Alliance for Genomics and Health](http://genomicsandhealth.org/), 
an international coalition, formed to enable the sharing of genomic and clinical data. It serves to provide a 
standardized API framework and data structure to allow for interoperability of datasets hosted at different institutions.
  
## Task Execution Service (TES)
The Task Execution Service (TES) API is an effort to define a standardized schema and API for describing batch 
execution tasks. A task defines a set of input files, a set of (Docker) containers and commands to run, a set of 
output files, and some other logging and metadata.

TES servers accept task documents and execute them asynchronously on available compute resources. A TES server 
could be built on top of a traditional HPC queuing system, such as Grid Engine, Slurm or cloud style compute systems
such as AWS Batch or Kubernetes.
  
## Compliance Document  
The compliance suite is designed as an abstract and API specification independent runner. It allows reusability 
of specs without having to make significant code changes. The suite is run via multiple YAML-based test files 
defining the test flow of an API endpoint. For more details, please refer the Architecture section.

This documentation is for implementers of TES servers. Implementers **MUST** adhere to this documentation 
during development of TES-compliant servers, as the compliance tests outlined herein conform with the 
[TES API specification](https://github.com/ga4gh/task-execution-schemas/blob/develop/openapi/task_execution_service.openapi.yaml).
The testing suite performs API testing on all routes discussed in the specification. TES server 
responses **MUST** comply with the proper YAML file format and response models for successful validation against each endpoint.