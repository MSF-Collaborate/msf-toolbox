# TopDeskIncidentClient

## Overview

`TopDeskIncidentClient` is a Python class designed to interact with the TopDesk Incident API. It provides methods to manage incidents, including retrieval and more.

## Features

- **Authentication**: Connect to the TopDesk API using your credentials.
- **Incident Management**: Retrieve, list, and manage incidents.

## Usage

### Initialization

To use the TopDesk Incident Client, you need the base URL for the TopDesk API and your authentication credentials (username and password).

```python
from msftoolbox.topdesk.data import TopDeskIncidentClient

client = TopDeskIncidentClient(
    topdesk_url="https://topdesk.example.com", 
    username="your-username", 
    password="your-password"
)
```

### Methods

#### List Incidents
Retrieve a list of incidents with optional filtering, pagination, sorting, and field selection.

```python
incidents = client.list_incidents(
    fiql_query="status==open", 
    offset=0, 
    page_size=10, 
    sort="creationDate:desc", 
    fields="id,number,briefDescription", 
    date_format="iso8601"
)
```

#### Get Incident
Retrieve an incident by its ID or number.

```python
incident = client.get_incident(incident_id="123456")
```

#### Get Incident Actions
Get actions associated with a specific incident.

```python
actions = client.get_incident_actions(
    incident_id="123456", 
    inlineimages=True
)
```

#### Get Incident Request
Retrieve a specific request related to an incident.

```python
request = client.get_incident_request(
    incident_id="123456", 
    inlineimages=True
)
```

### Utility Methods

#### Check Valid UUID
Verify if a given string is a valid UUID.

```python
is_valid = client.is_valid_uuid("123e4567-e89b-12d3-a456-426614174000")
```

### Notes

- **Error Handling**: The client raises exceptions for HTTP errors encountered during API requests.
- **Security**: Ensure your credentials are stored securely and not hardcoded in your scripts.