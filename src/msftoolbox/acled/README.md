# ACLEDClient

## Overview

`ACLEDClient` is a Python class designed to interact with the ACLED API, allowing for data extraction and filtering of conflict events, actors, regions, and countries. The documentation of the original API can be found here [documentation](https://developer.acleddata.com/rehd/cms/views/acled_api/documents/API-User-Guide.pdf)

## Features

- **Event Querying**: Retrieve a list of events with various filtering options such as date range, country, and actor.
- **Actor Listing**: Obtain a list of actors with filters based on name and event dates.
- **Region and Country Listing**: Access lists of regions and countries with optional filters.

## Usage

### Initialization

Initialize the `ACLEDClient` with your API key and email.

```python
from msftoolbox.acled.data import ACLEDClient

acled_client = ACLEDClient(
    api_key="your_api_key",
    email="your_email@example.com",
    limit=50,
    format="json"
)

```

### Methods
#### List Events
Retrieve a list of events with optional filters.

```python

events = acled_client.list_events(
    event_date="2024-01-01|2024-01-20",
    country="Lebanon",
    event_date_where="BETWEEN",
    limit=100
)

```
#### List Actors
Fetch a list of actors with optional filters.

```python

actors = acled_client.list_actors(
    actor_name="Government of Lebanon",
    limit=10
)

```
#### List Regions
Access a list of regions with optional filters.

```python

regions = acled_client.list_regions(
    region_name="Middle East"
)

```

#### List Countries
Get a list of countries with optional filters.

```python

countries = acled_client.list_countries(
    country="Lebanon"
)

```

#### Example Workflow
Initialize the Client: Set up the ACLEDClient with your credentials.
List Events: Fetch events based on specific criteria.
List Actors: Retrieve actors involved in events.

```python

# Initialize the client
acled_client = ACLEDClient(api_key="your_api_key", email="your_email@example.com")

# List events
events = acled_client.list_events(
    event_date="2024-01-01|2024-01-20",
    country="Lebanon",
    event_date_where="BETWEEN",
    limit=100
)

# List actors
actors = acled_client.list_actors(
    actor_name="Government of Lebanon",
    limit=10
)

```
## Error Handling
HTTP Errors: If the API request fails, an HTTPError is raised with the error details.
This class provides a comprehensive interface to the ACLED API, enabling efficient data extraction and filtering for conflict analysis and research.