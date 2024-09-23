from azure.identity import AzureCliCredential, DefaultAzureCredential
from azure.storage.blob import BlobServiceClient
import pandas as pd
import io


class AzureStorageAccountClient:
    def __init__(self, datalake_url, local_run=True):
        """
        Initialize the AzureDataLakeConnector with datalake_url and determine the credential type.

        Args:
            datalake_url (string): The URL of the storage account.
            local_run (bool): Flag to determine if running locally or in production.
        """
        self.datalake_url = datalake_url
        self.local_run = local_run
        self.credential = self._get_credential()
        self.blob_service_client = BlobServiceClient(account_url=self.datalake_url, credential=self.credential)

    def _get_credential(self):
        """
        Determine the credential type based on the local_run flag.

        Returns:
            credential (object): The credentials to be used for authentication.
        """
        if self.local_run:
            return AzureCliCredential()
        else:
            return DefaultAzureCredential()

    def connect_container(self, datalake_container_name):
        """
        Connect to a Blob container.

        Args:
            datalake_container_name (string): The name of the container in the storage account.

        Returns:
            ContainerClient: An instance of the ContainerClient class.
        """
        return self.blob_service_client.get_container_client(datalake_container_name)

    def download_blob_file_to_stream(self, container_client, datalake_path):
        """
        Download a blob file to a stream.

        Args:
            container_client (ContainerClient): An instance of the ContainerClient class.
            datalake_path (string): The name of the file to be downloaded.

        Returns:
            Blob: A stream containing the contents of the file.
        """
        blob_client = container_client.get_blob_client(datalake_path)
        return blob_client.download_blob()

    def download_blob_file(self, container_client, datalake_path, destination_path):
        """
        Download a blob file to a local file.

        Args:
            container_client (ContainerClient): An instance of the ContainerClient class.
            datalake_path (string): The name of the file to be downloaded.
            destination_path (string): The local file path where the blob will be downloaded.

        Returns:
            string: The path to the downloaded file.
        """
        with open(destination_path, "wb") as file:
            blob_client = container_client.get_blob_client(datalake_path)
            download_stream = blob_client.download_blob()
            file.write(download_stream.readall())
        return destination_path

    def upload_object_to_blob(self, container_client, temp_location, datalake_destination):
        """
        Upload an object to an Azure Blob location.

        Args:
            container_client (ContainerClient): An instance of the ContainerClient class.
            temp_location (string): The file path for the local file to be uploaded.
            datalake_destination (string): The destination path in the Data Lake.

        Returns: None
        """
        blob_client = container_client.get_blob_client(datalake_destination)
        with open(temp_location, "rb") as input_data:
            blob_client.upload_blob(data=input_data, overwrite=True)

    def list_files_in_folder(self, container_client, folder_path):
        """
        List files in a specific folder within a container.

        Args:
            container_client (ContainerClient): An instance of the ContainerClient class.
            folder_path (string): The path of the folder within the container.

        Returns:
            List: A list of file names in the specified folder.
        """
        blob_list = container_client.list_blobs(name_starts_with=folder_path)
        return [blob.name for blob in blob_list]

    def download_blob_file_to_dataframe(self, container_client, datalake_path, encoding='utf-8'):
        """
        Download a CSV blob file and convert it to a pandas DataFrame.

        Args:
            container_client (ContainerClient): An instance of the ContainerClient class.
            datalake_path (string): The name of the CSV file to be downloaded.

        Returns:
            DataFrame: A pandas DataFrame containing the contents of the CSV file.
        """
        download_stream = self.download_blob_file_to_stream(container_client, datalake_path)
        csv_content = download_stream.readall()
        return pd.read_csv(io.StringIO(csv_content.decode(encoding)))

