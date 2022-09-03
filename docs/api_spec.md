## API Specification

The TES API specification defines 5 API endpoints. These endpoints follow the RESTful service philosophy. 
They use JSON in requests and responses and standard HTTP/HTTPS for information transport.
  
* GET Service Info `/service-info` - Provides information about the service

* GET List Tasks `/tasks`  - List tasks tracked by the TES server.

* GET Task by ID `/tasks/{id}` - Get a single task, based on providing the exact task ID string.

* POST Create Task `/tasks` - Create a new task.

* POST Cancel Task `/tasks/{id}:cancel`  - Cancel a task based on providing an exact task ID.
  
The compliance suite currently supports the [TES API specification v1.0][res-tes-v1.0]. The latest TES API specifications 
are available [here][res-tes-latest].

## API Models
The API Models can be generated automatically via [Pydantic][res-pydantic], eliminating the need to write them everytime 
the specification are changed. Instead of JSON schema based validation, the compliance suite relies on 
the `Pydantic` validation approach.

## Generating Pydantic Models
To generate the models for a newer API specification version, the following steps need to be followed:

1. Install `datamodel-code-generator` library that generates pydantic models from just about any data source.
```base
pip install datamodel-code-generator
```
2. Save the API spec locally. Run the command and provide the YAML file as input.
```base
datamodel-codegen --input api_spec.yaml --output model.py
```

3. The converted Python Pydantic API models are present in the output `model.py` file. Now copy this file to the 
`compliance_suite/models` directory and rename it appropriately.

The official guide by Pydantic is also available [here][res-pydantic-gen].


[res-tes-v1.0]: <https://github.com/ga4gh/task-execution-schemas/blob/v1.0/openapi/task_execution_service.openapi.yaml>
[res-tes-latest]: <https://github.com/ga4gh/task-execution-schemas/blob/develop/openapi/task_execution_service.openapi.yaml>
[res-pydantic]: <https://pydantic-docs.helpmanual.io/>
[res-pydantic-gen]: <https://pydantic-docs.helpmanual.io/datamodel_code_generator/>
