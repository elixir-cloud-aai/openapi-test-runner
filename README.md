[![Coverage][badge-coverage]][badge-url-coverage]
[![Python 3.6][badge-python]](https://www.python.org)

# TES Compliance Suite

The TES Compliance Suite determines a server's compliance with the [TES API specification][res-tes-spec]. The specification has been developed by the [Global Alliance for Genomics and Health][res-ga4gh], an international coalition, formed to enable the sharing of genomic and clinical data. It serves to provide a standardized API framework and data structure to allow for interoperability of datasets hosted at different institutions.

## Description

The compliance suite is designed as an abstract and API specification independent runner. It allows reusability of specs without having to make significant code changes. The suite is run via multiple YAML-based test files defining the test flow of an API endpoint.

## Documentation

Please refer [Installation and Usage][res-doc-installation]  to get started with the installation and usage of suite.

You can also find more details about suite architecture and methodology.

- [Preamble](docs/preamble.md)
- [API Specification](docs/api_spec.md)
- [Architecture](docs/architecture.md)
- [Endpoint Test Flow](docs/endpoints.md)
- [Tests - Deep Analysis](docs/test_structure.md)
- [Report](docs/report.md)


## Contributing

This project is a community effort and lives off your contributions, be it in
the form of bug reports, feature requests, discussions, or fixes and other code
changes. Please refer to our organization's [contributing
guidelines][res-contributing] if you are interested to contribute.
Please mind the [code of conduct][res-coc] for all interactions
with the community.

## Versioning

The project adopts [semantic versioning][res-semver]. Currently, the service
is in alpha stage, so the API may change without further notice.

## Contact

The project is a collaborative effort under the umbrella of [ELIXIR Cloud &
AAI][res-elixir-cloud]. Follow the link to get in touch with us via chat or
email. Please mention the name of this service for any inquiry, proposal,
question etc.

![GA4GH_Logo_banner][img-logo-ga4gh]
![Elixir_Logo_banner][img-logo-elixir]

[badge-coverage]: <https://codecov.io/gh/elixir-cloud-aai/tes-compliance-suite/branch/dev/graph/badge.svg?branch=dev>
[badge-url-coverage]: <https://codecov.io/gh/elixir-cloud-aai/tes-compliance-suite?branch=dev>
[badge-python]: <https://img.shields.io/badge/python-3.8%20-blue.svg?style=flat-square>
[img-logo-elixir]: docs/images/img-elixir.svg
[img-logo-ga4gh]: docs/images/img-ga4gh.svg
[res-elixir-cloud]: <https://github.com/elixir-cloud-aai/elixir-cloud-aai>
[res-semver]: <https://semver.org/>
[res-contributing]: <https://github.com/elixir-cloud-aai/elixir-cloud-aai/blob/dev/CONTRIBUTING.md>
[res-coc]: <https://github.com/elixir-cloud-aai/elixir-cloud-aai/blob/dev/CODE_OF_CONDUCT.md>
[res-doc-installation]: docs/utility.md
[res-tes-spec]: <https://github.com/ga4gh/task-execution-schemas/blob/develop/openapi/task_execution_service.openapi.yaml>
[res-ga4gh]: <http://genomicsandhealth.org/>
