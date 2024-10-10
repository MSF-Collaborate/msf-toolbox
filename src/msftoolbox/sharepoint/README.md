# SharePointClient

## Overview

`SharePointClient` is a Python class designed to interact with the Office365 SharePoint API. It provides methods for authenticating, listing files and folders, downloading, uploading, moving, renaming, and recycling files, as well as creating folders.

## Features

- **Authentication**: Easily authenticate with SharePoint using your credentials.
- **File and Folder Management**: List, download, upload, move, rename, and recycle files. List and create folders.
- **Recursive Operations**: Recursively list files and folders within a directory. Please note that certain characters in URLs can cause issues such as "#".

## Usage

### Initialization

#### Using Client ID and Secret 
```python
from sharepoint_client import SharePointClient

client = SharePointClient(
    site_url="https://your-site-url",
    client_id="your-client-id",
    client_secret="your-client-secret"
)
```

#### Using Username and Password
Fails for MFA enabled accounts.

```python
from sharepoint_client import SharePointClient

client = SharePointClient(
    site_url="https://your-site-url", 
    username="your-username", 
    password="your-password"
    )
```

### Methods

#### List Files in a Folder

```python
files = client.list_files_in_folder(
    folder_url="/path/to/folder"
    )
```

#### List Folders in a Folder

```python
folders = client.list_folders_in_folder(
    folder_url="/path/to/folder"
    )
```

#### Download a File

```python
client.download_file(
    source_url="/path/to/file", 
    destination_file_path="local/path/to/save"
    )
```

#### Upload a File

```python
client.upload_file(
    source_file_path="local/path/to/file", 
    destination_url="/path/to/destination/folder"
    )
```

#### Move a File

```python
client.move_file_to_folder(
    source_file_url="/path/to/file", 
    destination_folder_url="/path/to/destination/folder"
    )
```

#### Rename a File

```python
client.rename_file(
    file_url="/path/to/file", 
    new_file_name="new-name.txt"
    )
```

#### Recycle a File

```python
client.recycle_file(
    file_url="/path/to/file"
    )
```

#### Create a Folder if Not Exists

```python
client.create_folder_if_not_exists(
    folder_url="/path/to/folder"
    )
```

#### Test Folder Existence

```python
exists = client.test_folder_existence(
    folder_url="/path/to/folder"
    )
```

### `keep_metadata` Parameter

The `keep_metadata` parameter is used in methods that list files or folders, such as `list_files_in_folder` and `list_folders_in_folder`. It determines the level of detail returned for each file or folder.

#### Usage

- **`keep_metadata=False`**: 
  - Returns a simplified list containing only essential information, such as the name, server-relative URL, and last modified time of each file or folder.
  - This option is useful when you need a quick overview without detailed properties.

- **`keep_metadata=True`**: 
  - Returns the full properties object for each file or folder, including all available metadata.
  - This option is ideal when you need comprehensive information about each item, such as size, author, or custom metadata fields.

