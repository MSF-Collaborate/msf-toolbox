# GDELTExtractor

## Overview

`GDELTExtractor` is a Python class designed to interact with the GDELT Project API. It provides methods for querying news reports, retrieving report content, and handling potential errors gracefully.

## Features

- **Report Querying**: Retrieve a list of news reports based on specified criteria such as date range, topic, and country.
- **Content Retrieval**: Download and parse the full content of news articles.
- **Error Handling**: Manage errors during article download and translation processes.

## Usage

### Initialization

```python
from msftoolbox.gdelt.articles import GDELTExtractor

client = GDELTExtractor(
    sort="HybridRel",
    limit=50,
    mode="ArtList"
)
```

### Methods

#### List Reports

Retrieve a list of news reports based on the specified parameters.

```python
reports = client.list_reports(
    start_date='2024-10-07',
    end_date='2024-10-14',
    query_value="Refugees",
    country_filter="Turkey"
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
client = GDELTExtractor()

# Define parameters
start_date = '2024-10-07'
end_date = '2024-10-14'
topic = "Refugees"
country = "Turkey"

# List reports
reports = client.list_reports(start_date, end_date, topic, country)

# Process each report
for report in reports:
        # Get the report text
        report_url = report['url']
        report_content = client.get_report(report_url)
        report['report_text'] = report_content
```
### Error Handling

- **Download Errors**: If downloading an article fails, the method returns `None` for the text.

This class provides a robust framework for extracting and processing news data from the GDELT Project, with built-in error handling to ensure smooth operation.