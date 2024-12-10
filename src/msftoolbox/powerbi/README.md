# PowerBIClient

## Overview

`PowerBIClient` is a Python class designed to interact with the Power BI REST API. It provides methods for authenticating, managing workspaces, reports, datasets, and users within Power BI.

## Features

- **Authentication**: Seamlessly authenticate with Power BI using your Azure credentials.
- **Workspace Management**: Retrieve and manage workspaces and users within them.
- **Report Management**: Access, export, import, clone, and delete reports.
- **Dataset Management**: Retrieve, refresh, and manage datasets and their users.
- **Token Verification**: Automatically verify and refresh authentication tokens as needed.

## Usage

### Connecting to the Power BI REST API
To connect to the Power BI REST API, you need to have a Microsoft account that has access to Power BI and an Azure AD application. With all that, you can connect to the Power BI REST API using the following function:

```python
from msftoolbox.powerbi.workspace import PowerBIClient

client = PowerBIClient(
    client_id="your-client-id",
    username="your-username",
    password="your-password",
    tenant_id="your-tenant-id",
    client_secret="your-client-secret"
)
```
### Third Party Credits
This Class includes code from [powerbi-rest-api-python](https://github.com/AntoineDW/powerbi-rest-api-python) by [AntoineDW](https://github.com/AntoineDW), which is licensed under the MIT License. The report_extractor has been taken from a blog [post](https://python.plainenglish.io/extracting-measures-and-fields-from-a-power-bi-report-in-python-1b928d9fb128). Written by [Umberto Grando](https://inzaniak.github.io/).