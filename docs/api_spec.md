## API Specification

The TES API specification defines 5 API endpoints. These endpoints follow the RESTful service philosophy. They use JSON in requests and responses and standard HTTP/HTTPS for information transport.
  
* GET Service Info `/service-info` - Provides information about the service

* GET List Tasks `/tasks`  - List tasks tracked by the TES server.

* GET Task by ID `/tasks/{id}` - Get a single task, based on providing the exact task ID string.

* POST Create Task `/tasks` - Create a new task.

* POST Cancel Task `/tasks/{id}:cancel`  - Cancel a task based on providing an exact task ID.
  
Detailed specifications regarding these APIs are available [here](https://github.com/ga4gh/task-execution-schemas/blob/develop/openapi/task_execution_service.openapi.yaml)

## API Models
The API Models are generated automatically via `Pydantic`, eliminating the need to write them everytime the specification are changed. Instead of JSON schema based validation, the compliance suite relies on the Pydantic validation approach.