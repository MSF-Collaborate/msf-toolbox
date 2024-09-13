from azure.mgmt.resource import ResourceManagementClient
from azure.keyvault.secrets import SecretClient
from azure.identity import AzureCliCredential, DefaultAzureCredential
from azure.storage.blob import BlobServiceClient
import pandas as pd
import io
import openai

class AzureKeyvault:
    def __init__(self, subscription_id, local_run=True):
        """
        Initialize the AzureConnector with subscription_id and determine the credential type.

        Parameters:
        - subscription_id (string): ID of the Azure Subscription
        - local_run (bool): Flag to determine if running locally or in production.
        """
        self.subscription_id = subscription_id
        self.local_run = local_run
        self.credential = self._get_credential()

    def _get_credential(self):
        """
        Determine the credential type based on the local_run flag.

        Returns:
        - credential (object): The credentials to be used for authentication.
        """
        if self.local_run:
            return AzureCliCredential()
        else:
            return DefaultAzureCredential()

    def connect_to_subscription(self):
        """
        Connect to Azure Subscription.

        Returns:
        - ResourceManagementClient: Client for managing resources.
        """
        client = ResourceManagementClient(self.credential, subscription_id=self.subscription_id)
        return client

    def get_keyvault_secret(self, keyvault_url, secret_name):
        """
        Get a secret from the Key Vault.

        Parameters:
        - keyvault_url (string): The URL of the Key Vault.
        - secret_name (string): The name of the secret in the Key Vault.

        Returns:
        - String: The secret value.
        """
        client = SecretClient(vault_url=keyvault_url, credential=self.credential)
        return client.get_secret(secret_name).value

    def list_keyvault_secrets(self, keyvault_url):
        """
        List all secrets in the Key Vault.

        Parameters:
        - keyvault_url (string): The URL of the Key Vault.

        Returns:
        - List: A list of secret names.
        """
        client = SecretClient(vault_url=keyvault_url, credential=self.credential)
        secrets = client.list_properties_of_secrets()
        return [secret.name for secret in secrets]
        
    def set_keyvault_secret(self, keyvault_url, secret_name, secret_value):
        """
        Set a secret in the Key Vault.

        Parameters:
        - keyvault_url (string): The URL of the Key Vault.
        - secret_name (string): The name of the secret to be set in the Key Vault.
        - secret_value (string): The value of the secret to be set in the Key Vault.

        Returns:
        - Secret: The newly created or updated secret.
        """
        client = SecretClient(vault_url=keyvault_url, credential=self.credential)
        secret = client.set_secret(secret_name, secret_value)
        return secret

    def delete_keyvault_secret(self, keyvault_url, secret_name):
        """
        Delete a secret from the Key Vault.

        Parameters:
        - keyvault_url (string): The URL of the Key Vault.
        - secret_name (string): The name of the secret to be deleted from the Key Vault.

        Returns:
        - DeletedSecret: The deleted secret.
        """
        client = SecretClient(vault_url=keyvault_url, credential=self.credential)
        deleted_secret = client.begin_delete_secret(secret_name).result()
        return deleted_secret

    def list_deleted_keyvault_secrets(self, keyvault_url, maxresults=None):
        """
        List deleted secrets in the Key Vault.

        Parameters:
        - keyvault_url (string): The URL of the Key Vault.
        - maxresults (int, optional): The maximum number of results to return.

        Returns:
        - List: A list of deleted secret names.
        """
        client = SecretClient(vault_url=keyvault_url, credential=self.credential)
        deleted_secrets = client.list_deleted_secrets(max_page_size=maxresults)
        return [secret.name for secret in deleted_secrets]

    def recover_keyvault_secret(self, keyvault_url, secret_name):
        """
        Recover a deleted secret in the Key Vault.

        Parameters:
        - keyvault_url (string): The URL of the Key Vault.
        - secret_name (string): The name of the secret to be recovered from the Key Vault.

        Returns:
        - Secret: The recovered secret.
        """
        client = SecretClient(vault_url=keyvault_url, credential=self.credential)
        recovered_secret = client.begin_recover_deleted_secret(secret_name).result()
        return recovered_secret

class AzureStorageAccount:
    def __init__(self, datalake_url, local_run=True):
        """
        Initialize the AzureDataLakeConnector with datalake_url and determine the credential type.

        Parameters:
        - datalake_url (string): The URL of the storage account.
        - local_run (bool): Flag to determine if running locally or in production.
        """
        self.datalake_url = datalake_url
        self.local_run = local_run
        self.credential = self._get_credential()
        self.blob_service_client = BlobServiceClient(account_url=self.datalake_url, credential=self.credential)

    def _get_credential(self):
        """
        Determine the credential type based on the local_run flag.

        Returns:
        - credential (object): The credentials to be used for authentication.
        """
        if self.local_run:
            return AzureCliCredential()
        else:
            return DefaultAzureCredential()

    def connect_container(self, datalake_container_name):
        """
        Connect to a Blob container.

        Parameters:
        - datalake_container_name (string): The name of the container in the storage account.

        Returns:
        - ContainerClient: An instance of the ContainerClient class.
        """
        return self.blob_service_client.get_container_client(datalake_container_name)

    def download_blob_file_to_stream(self, container_client, datalake_path):
        """
        Download a blob file to a stream.

        Parameters:
        - container_client (ContainerClient): An instance of the ContainerClient class.
        - datalake_path (string): The name of the file to be downloaded.

        Returns:
        - Blob: A stream containing the contents of the file.
        """
        blob_client = container_client.get_blob_client(datalake_path)
        return blob_client.download_blob()

    def download_blob_file(self, container_client, datalake_path, destination_path):
        """
        Download a blob file to a local file.

        Parameters:
        - container_client (ContainerClient): An instance of the ContainerClient class.
        - datalake_path (string): The name of the file to be downloaded.
        - destination_path (string): The local file path where the blob will be downloaded.

        Returns:
        - string: The path to the downloaded file.
        """
        with open(destination_path, "wb") as file:
            blob_client = container_client.get_blob_client(datalake_path)
            download_stream = blob_client.download_blob()
            file.write(download_stream.readall())
        return destination_path

    def upload_object_to_blob(self, container_client, temp_location, datalake_destination):
        """
        Upload an object to an Azure Blob location.

        Parameters:
        - container_client (ContainerClient): An instance of the ContainerClient class.
        - temp_location (string): The file path for the local file to be uploaded.
        - datalake_destination (string): The destination path in the Data Lake.

        Returns: None
        """
        blob_client = container_client.get_blob_client(datalake_destination)
        with open(temp_location, "rb") as input_data:
            blob_client.upload_blob(data=input_data, overwrite=True)

    def list_files_in_folder(self, container_client, folder_path):
        """
        List files in a specific folder within a container.

        Parameters:
        - container_client (ContainerClient): An instance of the ContainerClient class.
        - folder_path (string): The path of the folder within the container.

        Returns:
        - List: A list of file names in the specified folder.
        """
        blob_list = container_client.list_blobs(name_starts_with=folder_path)
        return [blob.name for blob in blob_list]

    def download_blob_file_to_dataframe(self, container_client, datalake_path, encoding='utf-8'):
        """
        Download a CSV blob file and convert it to a pandas DataFrame.

        Parameters:
        - container_client (ContainerClient): An instance of the ContainerClient class.
        - datalake_path (string): The name of the CSV file to be downloaded.

        Returns:
        - DataFrame: A pandas DataFrame containing the contents of the CSV file.
        """
        download_stream = self.download_blob_file_to_stream(container_client, datalake_path)
        csv_content = download_stream.readall()
        return pd.read_csv(io.StringIO(csv_content.decode(encoding)))

class AzureOpenAi:
    def __init__(self, open_ai_key, base_endpoint, api_version="2023-03-15-preview"):
        """
        Initialize the AzureOpenAi with the OpenAI API key and endpoint.

        Parameters:
        - open_ai_key (string): The API key for Azure OpenAI.
        - base_endpoint (string): The base endpoint URL for Azure OpenAI.
        - api_version (string): The API version to use (default is "2023-03-15-preview").
        """
        self.open_ai_key = open_ai_key
        self.base_endpoint = base_endpoint
        self.api_version = api_version
        self.open_ai_client = openai.AzureOpenAI(
            api_key=self.open_ai_key,
            api_version=self.api_version,
            azure_endpoint=self.base_endpoint
        )

    def chat_completions(self, model, system_content, user_content, temperature=0.3, max_tokens=1000, top_p=0.9, frequency_penalty=0, presence_penalty=0):
        """
        Send a chat completion request to the OpenAI API.

        Parameters:
        - model (string): The model to use for the completion.
        - system_content (string): The content for the system role.
        - user_content (string): The content for the user role.
        - temperature (float): Sampling temperature.
        - max_tokens (int): Maximum number of tokens to generate.
        - top_p (float): Nucleus sampling parameter.
        - frequency_penalty (float): Frequency penalty parameter.
        - presence_penalty (float): Presence penalty parameter.

        Returns:
        - dict: The response from the OpenAI API.
        """
        message = [
            {
                "role": "system",
                "content": system_content
            },
            {
                "role": "user",
                "content": user_content
            }
        ]

        response = self.open_ai_client.chat.completions.create(
            model=model,
            messages=message,
            temperature=temperature,
            max_tokens=max_tokens,
            top_p=top_p,
            frequency_penalty=frequency_penalty,
            presence_penalty=presence_penalty,
        )

        return response