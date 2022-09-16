## Endpoint Test Flow

Deciding the test flow is crucial while creating YAML test files. Different endpoints can be added as modules for
end-to-end real world scenario replication. The test flow for each TES API endpoint is described below. 
  

## GET Service Info

The service info endpoint is independent of others and can be invoked alone.

1. Get Service Info `GET /service-info`

## GET List Tasks

A task must be present while fetching the list of tasks. Hence, creating a task beforehand is necessary.

1. Create a new task  `POST /tasks`
2. Get list of tasks `GET /tasks`

## GET  Task by ID

A task must be present while fetching it. Hence, creating a task beforehand is necessary.

1. Create a new task  `POST /tasks`. The ID will be stored in auxiliary space.
2. Get the task by ID `GET /tasks/{id}`

## POST Create Task

A simple logical test would be just sending the request to create a new task. However, a more detailed validation
will be GET this task by ID and monitor the task status inside the TES server. If the task returns an appropriate
status from `["COMPLETE", "EXECUTOR_ERROR", "SYSTEM_ERROR"]`, then its successful.

1. Create a new task  `POST /tasks`. The ID will be stored in auxiliary space.
2. Get the task by ID `GET /tasks/{id}`

## POST Cancel Task

A task must be present in order to be canceled. Hence, creating a task beforehand is necessary. A simple logical
test would be just sending the request to cancel the task. However, a more detailed validation will be GET this
task by ID and monitor the task status inside the TES server. If the task returns an appropriate status
from `["CANCELED"]`, then its successful.

1. Create a new task  `POST /tasks`. The ID will be stored in auxiliary space.
2. Cancel the task `POST /tasks/{id}:cancel`
3. Get the task by ID `GET /tasks/{id}`