## Report

The report generated via the ga4gh-testbed-lib consists of Phases, Tests and Cases. In TES compliance suite, a phase refers to a YAML test file, a test to the type of test (e.g. YAML test or the individual job test) and a case refers to the validation check for each test. The report is finalized and generated in JSON format.

For a better view of the report, a local web server is run where the report is displayed over HTML views. The report headers display the `Report Specifications` which tell us about the compliance suite, platform and report standards. It also gives the test summary indicating how many test were successful or failure.

![Report_Headers](/docs/images/report_headers.JPG)

The reports consists of 3 tabs.

## Text view
This displays the report in textual view. It shows details of each phase, test and case. The status for each entity is present along with the message, details and logs.

![Report_Text](/docs/images/report_text.JPG)

## Table view
The concise table view contains the Phase, Test, Case and Result info. It helps in identifying the successful and failure test cases.

![Report_Table](/docs/images/report_table.JPG)

## JSON view
This displays the report in its JSON format to understand the field-value mapping. The report can be downloaded as well.

![Report_JSON](/docs/images/report_json.JPG)