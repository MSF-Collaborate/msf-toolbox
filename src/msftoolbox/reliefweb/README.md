# ReliefWebClient

## Overview

`ReliefWebClient` is a Python class designed to interact with the Relief Web Updates API. It provides methods for querying reports, retrieving report content, and parsing the data for further analysis or storage.

## Features

- **Report Querying**: Retrieve a list of reports based on specified criteria such as date range, keywords, and country.
- **Content Retrieval**: Download the full content of reports.
- **Error Handling**: Manage errors gracefully during data retrieval and parsing.

## Usage

### Initialization

```python
from msftoolbox.reliefweb.data import ReliefWebClient

client = ReliefWebClient(
    app_name="testing-rwapi",
    preset="latest",
    limit=50,
    profile="full"
)
```

### Methods
List Reports
Retrieve a list of reports based on the specified parameters. The country filter is based on country iso3 formats.

``` python
Copy code

reports = client.list_reports(
    start_date='2024-01-01',
    end_date='2024-10-14',
    query_value='refugees',
    countries_filter=['AFG']
)
```

### Get Report Content
Fetch and parse the full content of a report from its URL.

``` python

report_data = client.get_report(
    report_url="https://example.com/report"
)

```

### Example Workflow
List Reports: Fetch reports based on criteria.
Get Reports: Retrieve and process the report data.

``` python
# Initialize the client
client = ReliefWebClient()

# Define parameters
start_date = '2024-01-01'
end_date = '2024-10-14'
query_value = 'refugees'
countries_filter = ['AFG']

# List reports
reports = client.list_reports(
    start_date, 
    end_date, 
    query_value, 
    countries_filter=countries_filter
    )

# Process each report
for report in reports:
    report_url = report['url']
    report_data = client.get_report(report_url)
    print(report_data)

```

## Error Handling
HTTP Errors: If a request fails, an HTTPError is raised with the status code and error message.
This class provides a structured approach to extracting and processing data from the Relief Web Updates API, with built-in error handling to ensure reliable operation.