# KoboClient

## Overview

`KoboClient` is a Python class designed to interact with the [Kobo Toolbox API](https://support.kobotoolbox.org/). It provides methods for authenticating, listing surveys, extracting data and metadata from those surveys.

## Features

- **Authentication**: Easily authenticate with Kobo using your credentials.
- **Data Extraction**: Extract survey data and metadata about the survey's content

## Usage

### Initialization

#### Using API Token

To use the Kobo Client you need an API token. This API token can be obtained by going to https://[kpi-url]/token/?format=json.  The base URL (kpi-url) depends on the server you are using: for most users it is kf.kobotoolbox.org or eu.kobotoolbox.org. Find more methods [here](https://support.kobotoolbox.org/api.html)

```python
from kobo_client import KoboClient

client = KoboClient(
    base_url="https://kobo.example.com/", 
    api_token="your-token"
    )
```

### Methods

#### List Assets
Retrieve a list of all assets (/surveys) from the Kobo API, available for this user.

```python
surveys = client.list_assets()
```

#### Get Asset UID
Get the asset UID based on the asset name. The asset ID is required for all interactions with a specific asset.
The asset name can be found in the Kobo user interface (referred to as 'Project Name') . For example:

![image](https://github.com/user-attachments/assets/00ae1829-f992-4a66-8404-03e8c52c22bc)

```python
asset_uid = client.get_asset_uid(
    asset_name="Hand Hygiene Observation Tool"
    )
```

#### Get Asset
Retrieve a specific asset from the Kobo API. Can be used in combination with get_asset_choice_items to extract answer labels.

```python
asset_dict = client.get_asset(asset_uid = 'gh3NsxvpoBmltERFuKcVnD')  
```

#### Get Asset Data
Retrieve all data for a specific Kobo asset. This function is set up to handle pagination in the API response. The Kobo server has a limit of returning 30.000 records per page. The function loops through the pages and combines all data in a list of dictionaries with the results.

```python
asset_list = client.get_asset_data(asset_uid = 'gh3NsxvpoBmltERFuKcVnD')  
```

The resulting asset list can be converted into a Pandas Datframe.
```python
import pandas as pd
asset_df = pd.json_normalize(asset_list)  
```
#### Get Asset Metadata
Extracts labels and related metadata from a specified asset. This function can be used to retrieve the structure of the survey (What questions were asked, how were the questions grouped etc.) It returns all questions in the survey, their group, label (i.e. full question text, can be in multiple languages), including system-generated entries (e.g. SURVEY_START_TIME).

```python
asset_metadata_list = client.get_asset_metadata(asset_uid = 'gh3NsxvpoBmltERFuKcVnD')  
```

#### Get Asset Choice Items
This function extracts choice items from an asset dictionary, pulling out key details like the list name, item name, and label. It's useful for obtaining the choice items used in a survey, essentially identifying which answer options were presented for each question. The function returns all possible answers in the survey along with their labels, which include the full answer text and can be available in multiple languages.

```python
asset_choice_item_list = client.get_asset_choice_items(asset_uid = 'gh3NsxvpoBmltERFuKcVnD')
```

