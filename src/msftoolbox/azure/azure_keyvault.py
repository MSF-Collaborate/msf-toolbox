from typing import Optional
from azure.keyvault.secrets import SecretClient
from azure.identity import AzureCliCredential, DefaultAzureCredential, ManagedIdentityCredential

class AzureKeyvaultClient:
    """
    A class to interact with an Azure Key Vault.

    This class provides methods to send, read, and delete secrets in Azure Key Vault.
    """
    def __init__(
        self,
        keyvault_url: str,
        local_run: bool = True,
        managed_identity_client_id: str = None
        ):
        """
        Initialize the AzureConnector with subscription_id and determine the credential type.

        Args:
            keyvault_url (string): The URL of the Key Vault.
            local_run (bool): Flag to determine if running locally or in production.
            managed_identity_client_id (str): The managed_identity_client_id required for ManagedIdentityCredentials
        """
        self.local_run = local_run
        self.managed_identity_client_id = managed_identity_client_id
        self.credential = self._get_credential()
        self.keyvault_url = keyvault_url
        self.keyvault_client = SecretClient(
            vault_url=self.keyvault_url,
            credential=self.credential
            )

    def _get_credential(
        self
        ):
        """
        Determine the credential type based on the local_run flag.

        Returns:
            credential (object): The credentials to be used for authentication.
        """
        if self.local_run:
            return AzureCliCredential()
        elif self.managed_identity_client_id is not None:
            return ManagedIdentityCredential(
                client_id = self.managed_identity_client_id
                )
        else:
            return DefaultAzureCredential()


    def get_keyvault_secret_value(
        self,
        secret_name: str
        ):
        """
        Get a secret from the Key Vault.

        Args:
            secret_name (string): The name of the secret in the Key Vault.

        Returns:
            String: The secret value.
        """
        secret_value = self.keyvault_client.get_secret(
            secret_name
            ).value

        return secret_value

    def list_secret_names(
        self
        ):
        """
        List all secrets in the Key Vault.

        Returns:
            List: A list of secret names.
        """

        secrets = self.keyvault_client.list_properties_of_secrets()
        return [secret.name for secret in secrets]

    def set_keyvault_secret_value(
        self,
        secret_name: str,
        secret_value: str
        ):
        """
        Set a secret in the Key Vault.

        Args:
            secret_name (string): The name of the secret to be set in the Key Vault.
            secret_value (string): The value of the secret to be set in the Key Vault.

        Returns:
            Secret: The newly created or updated secret.
        """
        secret = self.keyvault_client.set_secret(
            secret_name,
            secret_value
            )

        return secret

    def delete_keyvault_secret(
        self,
        secret_name: str
        ):
        """
        Delete a secret from the Key Vault.

        Args:
            secret_name (string): The name of the secret to be deleted from the Key Vault.

        Returns:
            DeletedSecret: The deleted secret.
        """
        deleted_secret = self.keyvault_client.begin_delete_secret(
            secret_name
            ).result()

        return deleted_secret

    def list_deleted_keyvault_secrets(
        self,
        maxresults: Optional[int]=None
        ):
        """
        List deleted secrets in the Key Vault.

        Args:
            maxresults (int, optional): The maximum number of results to return.

        Returns:
            List: A list of deleted secret names.
        """
        deleted_secrets = self.keyvault_client.list_deleted_secrets(
            max_page_size=maxresults
            )

        return [secret.name for secret in deleted_secrets]

    def recover_keyvault_secret(
        self,
        secret_name: str
        ):
        """
        Recover a deleted secret in the Key Vault.

        Args:
            secret_name (string): The name of the secret to be recovered from the Key Vault.

        Returns:
            Secret: The recovered secret.
        """
        recovered_secret = self.keyvault_client.begin_recover_deleted_secret(
            secret_name
            ).result()

        return recovered_secret
