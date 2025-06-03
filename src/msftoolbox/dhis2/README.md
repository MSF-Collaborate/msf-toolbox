# Dhis2MetadataClient

## Overview

`Dhis2MetadataClient` is a Python class designed to interact with the DHIS2 API, allowing for data extraction and management of metadata such as organization units, data sets, programs, and indicators. This client supports authentication via username/password or personal access token.

## Features

- **Authentication:** Supports both username/password and personal access token for secure API access.
- **Organization Unit Management:** Retrieve organization units and their children with various filtering options.
- **Data Set and Program Querying:** Access lists of data sets, programs, indicators, and other metadata elements.
- **Metadata Export:** Export metadata from the DHIS2 server for comprehensive data analysis.

## Usage

### Initialization

Initialize the `Dhis2MetadataClient` with your DHIS2 server credentials and URL.

```python
from dhis2_metadata_client import Dhis2MetadataClient

# Using username and password
client = Dhis2MetadataClient(
    username='your_username',
    password='your_password',
    server_url='https://your-dhis2-instance.org'
)

# Or using a personal access token
client = Dhis2MetadataClient(
    personal_access_token='your_personal_access_token',
    server_url='https://your-dhis2-instance.org'
)
```

### Methods

#### Get Organization Units

Retrieve a list of organization units with optional filters.

```python
org_units = client.get_organisation_units(level=2)
```

#### Get Data Sets

Fetch a list of data sets with optional filters.

```python
data_sets = client.get_datasets()
```

#### Get Programs

Access a list of programs with optional filters.

```python
programs = client.get_programs()
```

#### Get Indicators

Retrieve a list of indicators with optional filters.

```python
indicators = client.get_indicators()
```

#### Export Metadata

Export metadata from the DHIS2 server:

```python
metadata = client.export_metadata()
```

### Example Workflow

1. **Initialize the Client:** Set up the `Dhis2MetadataClient` with your credentials.
2. **List Organization Units:** Fetch organization units based on specific criteria.
3. **List Data Sets:** Retrieve data sets available in the DHIS2 instance.

```python
# Initialize the client
client = Dhis2MetadataClient(
    username='your_username',
    password='your_password',
    server_url='https://your-dhis2-instance.org'
)

# List organization units
org_units = client.get_organisation_units(level=2)

# List data sets
data_sets = client.get_datasets()
```

### Error Handling

- **Authentication Errors:** If authentication fails, a `ValueError` is raised with details.
- **HTTP Errors:** For other HTTP errors, an `HTTPError` is raised, providing error specifics.

This class provides a comprehensive interface to the DHIS2 API, enabling efficient metadata management and data extraction for health information systems and research.