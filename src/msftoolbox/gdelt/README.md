# GDELTClient

## Overview

`GDELTClient` is a Python class designed to interact with the GDELT Project API. It provides methods for querying news reports, retrieving report content, and handling potential errors gracefully.

## Features

- **Report Querying**: Retrieve a list of news reports based on specified criteria such as date range, topic, and country.
- **Content Retrieval**: Download and parse the full content of news articles.
- **Error Handling**: Manage errors during article download.

## Usage

### Initialization

```python
from msftoolbox.gdelt.data import GDELTClient

client = GDELTClient(
    sort="HybridRel",
    limit=10
)
```

### Methods

#### List Reports

Retrieve a list of news reports based on the specified parameters.

```python
report_list = gdelt_client.list_reports(
    start_date='2024-10-07',
    end_date='2024-10-14',
    query_value="healthcare",
    source_languages_filter=["english"],
    source_countries_filter=["bangladesh", "india"],
    source_domains_filter=None
    )
```

#### Get Report Content

Fetch and parse the full text of a news article from its URL.

```python
report_content = client.get_report(
    report_url="https://example.com/article"
)
```


### Example Workflow

1. **List Reports**: Fetch reports based on criteria.
2. **Handle Errors**: Manage any errors during the process.

```python
# Initialize the client
client = GDELTClient()

# Define parameters
start_date = '2024-09-07'
end_date = '2024-10-14'
topic = "Refugees"
source_countries_filter = ["Turkey"]

# List reports
reports = client.list_reports(
    start_date, 
    end_date, 
    topic, 
    source_countries_filter=source_countries_filter
    )

# Process each report
for report in reports:
        # Get the report text
        report_url = report['url']
        report_content = client.get_report(report_url)
        report['report_text'] = report_content
```
### Error Handling

- **Listing Errors**: If listing articles fails, the method returns a dictionary with the message text, exposing errors or lack of articles.
- **Download Errors**: If downloading an article fails, the method returns `None` for the text.

This class provides a robust framework for extracting and processing news data from the GDELT Project, with built-in error handling to ensure smooth operation.