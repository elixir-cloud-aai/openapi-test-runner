# Creates a Docker image that is ready to execute tes compliance suite

FROM python:3.8-slim AS build-env

WORKDIR /app

# Install TES Compliance suite dependencies
# Git is needed for the clone and jq is helpful with parsing results if needed
ENV DEBIAN_FRONTEND=noninteractive
RUN apt update
RUN apt -y install git jq

RUN git clone https://github.com/elixir-cloud-aai/openapi-test-runner.git

# Install TES Compliance suite
WORKDIR /app/openapi-test-runner
RUN python3.8 setup.py install

# Precreate results directory
RUN mkdir results

# Copy over specific instructions around how to run the tests
COPY entrypoint.sh /app/openapi-test-runner/entrypoint.sh

# If using entrpyoint script with no edits, set TES endpoint url here
ENV TES_ENDPOINT_URL=http://localhost/

ENTRYPOINT ["/bin/bash", "entrypoint.sh"]