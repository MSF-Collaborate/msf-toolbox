from azure.mgmt.resource import ResourceManagementClient
from azure.keyvault.secrets import SecretClient
from azure.identity import AzureCliCredential, DefaultAzureCredential

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

# Example usage:
# subscription_id = 'your_subscription_id'
# local_run = True  # Set to False if running in production
# azure_connector = AzureConnector(subscription_id, local_run)
# resource_client = azure_connector.connect_to_subscription()
# secret_value = azure_connector.get_keyvault_secret('https://your-keyvault-url.vault.azure.net/', 'your_secret_name')
