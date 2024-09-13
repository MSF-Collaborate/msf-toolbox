from azure.mgmt.resource.resources import ResourceManagementClient
from azure.keyvault.secrets import SecretClient

class AzureKeyvault:
    def __init__(self, subscription_id, credential):
        """
        Initialize the AzureConnector with subscription_id and credential.

        Parameters:
        - subscription_id (string): ID of the Azure Subscription
        - credential (object): The credentials to be used for authentication.
        """
        self.subscription_id = subscription_id
        self.credential = credential

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
