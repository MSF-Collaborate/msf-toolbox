# UniDataAPIClient

## Overview

`UniDataAPIClient` is a Python class designed to interact with the UniData API. It provides methods for configuring server credentials, making authenticated requests, and retrieving various types of data such as articles, subcatalogues, intros, and checklists.

## Features

- **Server Configuration**: Easily update and manage server credentials and URL.
- **Data Retrieval**: Fetch articles, subcatalogues, intros, and checklists with optional filtering.
- **Error Handling**: Handle authentication and HTTP errors gracefully.

## Usage

### Initialization

```python
from msftoolbox.unidata.data import UniDataAPIClient import UniDataAPIClient

client = UniDataAPIClient(
    username="your_username",
    password="your_password",
    server_url="https://api.unidata.example.com",
    timeout=10
)
```

### Methods
Configure UniData Server
Update the UniData server credentials and URL.

#### Get Articles
Retrieve a list of articles with optional query parameters.

```python

articles = client.get_articles(
    mode=0,
    formercode="ABC123",
    filter="//some/xpath",
    links=1,
    publishonweb=True,
    size=20,
    page=1
)
```

#### Get Subcatalogues
Fetch subcatalogues data from the UniData API.

``` python

subcatalogues = client.get_subcatalogues()
```

#### Get Intros
Retrieve intros data from the UniData API.

``` python

intros = client.get_intros()
```
#### Get Checklists
Fetch checklists data from the UniData API.

``` python

checklists = client.get_checklists()
```

#### Example Workflow
Initialize the Client: Set up the client with server credentials.
Fetch Articles: Retrieve and process articles data.

``` python
# Initialize the client
from msftoolbox.unidata.data import UniDataAPIClient import UniDataAPIClient

client = UniDataAPIClient(
    username="your_username",
    password="your_password",
    server_url="https://api.unidata.example.com"
)

# Fetch articles using a specific mode
mode = 4
page = 1
all_rows = []

import json

mode = 4
page = 1
all_rows = []

while True:
    articles = client.get_articles(mode=mode, size=100, page=page)
    rows = articles.get("rows", [])

    for row in rows:
        row['page_number'] = page
    all_rows.extend(rows)

    print(f"Processing page {page} with {len(rows)} articles.")
    page += 1
    
```

## Error Handling
Authentication Errors: Raises a ValueError if authentication fails due to incorrect credentials.
HTTP Errors: Raises an HTTPError for other HTTP-related issues, providing the status code and error message.
This class offers a structured approach to interacting with the UniData API, ensuring efficient data retrieval with robust error handling for reliable operation.