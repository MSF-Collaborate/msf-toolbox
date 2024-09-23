from azure.mgmt.resource import ResourceManagementClient
from azure.keyvault.secrets import SecretClient
from azure.identity import AzureCliCredential, DefaultAzureCredential

class AzureKeyvaultClient:
    def __init__(self, subscription_id, local_run=True):
        """
        Initialize the AzureConnector with subscription_id and determine the credential type.

        Args:
            subscription_id (string): ID of the Azure Subscription
            local_run (bool): Flag to determine if running locally or in production.
        """
        self.subscription_id = subscription_id
        self.local_run = local_run
        self.credential = self._get_credential()

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

    def connect_to_subscription(self):
        """
        Connect to Azure Subscription.

        Returns:
            ResourceManagementClient: Client for managing resources.
        """
        client = ResourceManagementClient(self.credential, subscription_id=self.subscription_id)
        return client

    def get_keyvault_secret(self, keyvault_url, secret_name):
        """
        Get a secret from the Key Vault.

        Args:
            keyvault_url (string): The URL of the Key Vault.
            secret_name (string): The name of the secret in the Key Vault.

        Returns:
            String: The secret value.
        """
        client = SecretClient(vault_url=keyvault_url, credential=self.credential)
        return client.get_secret(secret_name).value

    def list_keyvault_secrets(self, keyvault_url):
        """
        List all secrets in the Key Vault.

        Args:
            keyvault_url (string): The URL of the Key Vault.

        Returns:
            List: A list of secret names.
        """
        client = SecretClient(vault_url=keyvault_url, credential=self.credential)
        secrets = client.list_properties_of_secrets()
        return [secret.name for secret in secrets]
        
    def set_keyvault_secret(self, keyvault_url, secret_name, secret_value):
        """
        Set a secret in the Key Vault.

        Args:
            keyvault_url (string): The URL of the Key Vault.
            secret_name (string): The name of the secret to be set in the Key Vault.
            secret_value (string): The value of the secret to be set in the Key Vault.

        Returns:
            Secret: The newly created or updated secret.
        """
        client = SecretClient(vault_url=keyvault_url, credential=self.credential)
        secret = client.set_secret(secret_name, secret_value)
        return secret

    def delete_keyvault_secret(self, keyvault_url, secret_name):
        """
        Delete a secret from the Key Vault.

        Args:
            keyvault_url (string): The URL of the Key Vault.
            secret_name (string): The name of the secret to be deleted from the Key Vault.

        Returns:
            DeletedSecret: The deleted secret.
        """
        client = SecretClient(vault_url=keyvault_url, credential=self.credential)
        deleted_secret = client.begin_delete_secret(secret_name).result()
        return deleted_secret

    def list_deleted_keyvault_secrets(self, keyvault_url, maxresults=None):
        """
        List deleted secrets in the Key Vault.

        Args:
            keyvault_url (string): The URL of the Key Vault.
            maxresults (int, optional): The maximum number of results to return.

        Returns:
            List: A list of deleted secret names.
        """
        client = SecretClient(vault_url=keyvault_url, credential=self.credential)
        deleted_secrets = client.list_deleted_secrets(max_page_size=maxresults)
        return [secret.name for secret in deleted_secrets]

    def recover_keyvault_secret(self, keyvault_url, secret_name):
        """
        Recover a deleted secret in the Key Vault.

        Args:
            keyvault_url (string): The URL of the Key Vault.
            secret_name (string): The name of the secret to be recovered from the Key Vault.

        Returns:
            Secret: The recovered secret.
        """
        client = SecretClient(vault_url=keyvault_url, credential=self.credential)
        recovered_secret = client.begin_recover_deleted_secret(secret_name).result()
        return recovered_secret

