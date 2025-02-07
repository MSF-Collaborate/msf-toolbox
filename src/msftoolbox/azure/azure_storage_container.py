from azure.identity import AzureCliCredential, DefaultAzureCredential, ManagedIdentityCredential
from azure.storage.blob import BlobServiceClient
from typing import Union, List
import pandas as pd
import io


class AzureStorageContainerClient:
    def __init__(
        self,
        storage_account_url: str,
        container_name: str,
        local_run: bool = True,
        managed_identity_client_id: str = None,
        account_key: str = None
        ):
        """
        Initialize the AzureDataLakeConnector with datalake_url and determine the credential type.

        Args:
            storage_account_url (string): The URL of the storage account.
            container_name (string): The name of the container in the storage account.
            local_run (bool): Flag to determine if running locally or in production.
            managed_identity_client_id (str): The managed_identity_client_id required for ManagedIdentityCredentials.
            account_key (str): The storage account access key for authentication.
        """
        self.local_run = local_run
        self.managed_identity_client_id = managed_identity_client_id
        self.storage_account_url = storage_account_url
        self.container_name = container_name
        self.account_key = account_key
        self.credential = self._get_credential()

        blob_service_client = BlobServiceClient(
            account_url=self.storage_account_url,
            credential=self.credential
        )

        self.container_client = blob_service_client.get_container_client(
            self.container_name
        )

    def _get_credential(self):
        """
        Determine the credential type based on the provided parameters.

        Returns:
            credential (object): The credentials to be used for authentication.
        """
        if self.account_key:
            return self.account_key
        elif self.local_run:
            return AzureCliCredential()
        elif self.managed_identity_client_id is not None:
            return ManagedIdentityCredential(
                client_id=self.managed_identity_client_id
            )
        else:
            return DefaultAzureCredential()

    def download_blob_file_to_stream(
        self,
        datalake_path: str
        ):
        """
        Download a blob file to a stream.

        Args:
            datalake_path (string): The name of the file to be downloaded.

        Returns:
            Blob: A stream containing the contents of the file.
        """
        blob_client = self.container_client.get_blob_client(
            datalake_path
            )

        return blob_client.download_blob()

    def download_blob_file(
        self,
        datalake_path: str,
        destination_path: str
        ):
        """
        Download a blob file to a local file.

        Args:
            datalake_path (string): The name of the file to be downloaded.
            destination_path (string): The local file path where the blob will be downloaded.

        Returns:
            string: The path to the downloaded file.
        """
        with open(destination_path, "wb") as file:

            blob_client = self.container_client.get_blob_client(
                datalake_path
                )

            download_stream = blob_client.download_blob()
            file.write(download_stream.readall())


    def upload_object_to_blob(
        self,
        temp_location: str,
        datalake_destination: str
        ):
        """
        Upload an object to an Azure Blob location.

        Args:
            temp_location (string): The file path for the local file to be uploaded.
            datalake_destination (string): The destination path in the Data Lake.

        Returns: None
        """
        blob_client = self.container_client.get_blob_client(
            datalake_destination
            )

        with open(temp_location, "rb") as input_data:
            blob_client.upload_blob(
                data=input_data,
                overwrite=True
                )
        

    def list_files_in_folder(
        self,
        folder_path: str
        ):
        """
        List files in a specific folder within a container.

        Args:
            folder_path (string): The path of the folder within the container.

        Returns:
            List: A list of file names in the specified folder.
        """
        blob_list = self.container_client.list_blobs(
            name_starts_with=folder_path
            )

        return [blob.name for blob in blob_list]

    def download_blob_file_to_dataframe(
        self,
        datalake_path: str,
        encoding="utf-8"
        ):
        """
        Download a CSV blob file and convert it to a pandas DataFrame.

        Args:
            datalake_path (string): The name of the CSV file to be downloaded.

        Returns:
            DataFrame: A pandas DataFrame containing the contents of the CSV file.
        """
        download_stream = self.download_blob_file_to_stream(
            datalake_path
            )

        csv_content = download_stream.readall()
        return pd.read_csv(
            io.StringIO(csv_content.decode(encoding))
            )

    def delete_files(
        self,
        file_paths: Union[str, List[str]]
        ):
        """
        Deletes a list of blobs

        Args:
            file_paths (Union[str, List[str]]): A file path or list of file paths to delete in the container
        """
        if isinstance(file_paths, str):
            # Convert single string to a list
            file_paths = [file_paths]

        # Now file_paths is always a list, process it
        self.container_client.delete_blobs(*file_paths)