
from typing import Optional

import requests
import datetime
import logging

log = logging.getLogger()

class PowerBIClient:
    """
    A class to interact with the Power BI REST API.

    This class provides methods to authenticate and interact with the Power BI REST API, including
    managing workspaces, reports, datasets, and users.

    Attributes:
        client_id (str): The client ID of the Azure App Registration.
        username (str): The username of the account used to connect to Power BI.
        password (str): The password of the account used to connect to Power BI.
        tenant_id (str): The tenant ID of the Azure Active Directory where the App Registration is defined.
        client_secret (str): The client secret associated with the Azure App Registration.
        token (dict): A dictionary containing the bearer token and its expiration time.
    """

    def __init__(self, client_id, username, password, tenant_id, client_secret):
        """
        Initializes an instance of the PowerBI class.

        Args:
            client_id (str): The client ID of the Azure App Registration.
            username (str): The username of the account used to connect to Power BI.
            password (str): The password of the account used to connect to Power BI.
            tenant_id (str): The tenant ID of the Azure Active Directory where the App Registration is defined.
            client_secret (str): The client secret associated with the Azure App Registration.

        Returns:
            None
        """
        # Store params
        self.client_id = client_id
        self.username = username
        self.password = password
        self.tenant_id = tenant_id
        self.client_secret = client_secret
        self.token = {"bearer": None, "expiration": None}

    def connect(
        self,
        client_id: Optional[str] = None,
        username: Optional[str] = None,
        password: Optional[str] = None,
        tenant_id: Optional[str] = "common",
        client_secret: Optional[str] = None,
        ) -> None:
        """
        Connects to the Power BI REST API.

        Args:
            client_id (str, optional): The client id of the app registration within your Azure Tenant.
            username (str, optional): The username.
            password (str, optional): The password.
            tenant_id (str, optional): The tenant id. Default is "common".
            client_secret (str, optional): The client secret. Default is None.

        Returns:
            None
        """

        # Use provided parameters or fall back to instance variables
        self.client_id = client_id if client_id is not None else self.client_id
        self.username = username if username is not None else self.username
        self.password = password if password is not None else self.password
        self.tenant_id = tenant_id if tenant_id is not None else self.tenant_id
        self.client_secret = client_secret if client_secret is not None else self.client_secret

        if self.client_secret:
            body = {
                "grant_type": "password",
                "resource": "https://analysis.windows.net/powerbi/api",
                "client_id": self.client_id,
                "client_secret": self.client_secret,
                "username": self.username,
                "password": self.password,
            }
        else:
            body = {
                "grant_type": "password",
                "resource": "https://analysis.windows.net/powerbi/api",
                "client_id": self.client_id,
                "username": self.username,
                "password": self.password,
            }

        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        response = requests.post(
            f"https://login.microsoftonline.com/{self.tenant_id}/oauth2/token",
            headers=headers,
            data=body,
        )

        if response.status_code == 200:
            self.set_token(response.json()["access_token"])
            log.info("Connected to the Power BI REST API with %s", self.username)
        else:
            self.token["bearer"] = None
            self.token["expiration"] = None
            log.error(
                "Error %s -- Something went wrong when trying to retrieve the token from the REST API",
                    response.status_code
                )

    def verify_token(self) -> bool:
        """
        Verifies if the token is valid.

        Returns:
            bool: True if the token is valid, False otherwise.
        """
        if self.token["bearer"] is None:
            log.error("Error 401 -- Please connect to the Power BI REST API with the connect() function before")
            return False
        else:
            if self.token["expiration"] is None or self.token["expiration"] < datetime.datetime.now():
                self.connect()
                return True
            else:
                return True

    def get_token(self) -> dict:
        """
        Retrieves the token.

        Returns:
            dict: The token.
        """
        return self.token

    def set_token(self, bearer: str) -> None:
        """
        Sets the token.

        Args:
            bearer (str): The bearer token.

        Returns:
            None
        """
        self.token["bearer"] = f"Bearer {bearer}"
        self.token["expiration"] = datetime.datetime.now() + datetime.timedelta(hours=1)

    def get_workspace(self, workspace_id: str) -> list:
        """
        Retrieves the Power BI workspace with the specified ID.

        Args:
            workspace_id (str): The ID of the workspace to retrieve.

        Returns:
            list: The details of the retrieved workspace, or None if the workspace
                could not be found or there was an error.

        This function first verifies the authentication token using the `verify_token` method.
        If the token is valid, it sends a GET request to the Power BI API to retrieve a list
        of all workspaces. It then searches for the workspace with the specified ID and returns
        its details as a dictionary. If the workspace cannot be found, it returns None. If there
        is an error during the request or authentication process, it logs an error and returns None.

        """
        if not self.verify_token():
            return None

        headers = {"Authorization": self.token["bearer"]}
        response = requests.get("https://api.powerbi.com/v1.0/myorg/groups", headers=headers)

        if response.status_code == 200:
            workspace = [result for result in response.json()["value"] if result["id"] == workspace_id]
            if len(workspace) > 0:
                return workspace[0]
            else:
                return None
        else:
            log.error(
                "Error %s -- Something went wrong when trying to retrieve the workspace %s",
                    response.status_code, workspace_id
                )
            return None

    def get_workspaces(self) -> list:
        """
        Retrieves a list of all available Power BI workspaces.

        Returns:
            list: A list of dictionaries containing the details of each workspace,
                or None if there was an error.

        This function first verifies the authentication token using the `verify_token` method.
        If the token is valid, it sends a GET request to the Power BI API to retrieve a list
        of all workspaces. It returns the list of workspaces as a list of dictionaries. If there
        is an error during the request or authentication process, it logs an error and returns None.

        """
        if not self.verify_token():
            return None

        headers = {"Authorization": self.token["bearer"]}
        response = requests.get("https://api.powerbi.com/v1.0/myorg/groups", headers=headers)

        if response.status_code == 200:
            return response.json()["value"]
        else:
            log.error(
                "Error %s -- Something went wrong when trying to retrieve the list of workspaces you have access",
                    response.status_code
                )
            return None

    def get_users_in_workspace(self, workspace_id: str) -> list:
        """
        Retrieves a list of users in the specified Power BI workspace.

        Args:
            workspace_id (str): The ID of the workspace to retrieve the users from.

        Returns:
            list: A list of dictionaries containing the details of each user in the workspace,
                or None if there was an error.

        This function first verifies the authentication token using the `verify_token` method.
        If the token is valid, it sends a GET request to the Power BI API to retrieve a list of
        users in the specified workspace. It returns the list of users as a list of dictionaries.
        If there is an error during the request or authentication process, it logs an error and
        returns None.

        """
        if not self.verify_token():
            return None

        headers = {"Authorization": self.token["bearer"]}
        response = requests.get(
            f"https://api.powerbi.com/v1.0/myorg/groups/{workspace_id}/users",
            headers=headers
        )

        if response.status_code == 200:
            return response.json()
        else:
            log.error(
                "Error %s -- Something went wrong when trying to retrieve the list of users in the workspace %s",
                    response.status_code, workspace_id
                )
            return None

    def add_user_to_workspace(self, workspace_id: str, email: str, access: str = "Member") -> dict:
        """
        Adds a user to a workspace with the specified access level.

        Args:
            workspace_id (str): The ID of the workspace.
            email (str): The email address of the user to be added.
            access (str, optional): The access level for the user. Default is "Member".

        Returns:
            dict: A dictionary with the response code if the user was successfully added, otherwise None.

        Raises:
            None
        """
        if not self.verify_token():
            return None

        if access in ["Admin", "Contributor", "Member"]:
            headers = {"Authorization": self.token["bearer"]}
            body = {"userEmailAddress": email, "groupUserAccessRight": access}
            response = requests.post(
                f"https://api.powerbi.com/v1.0/myorg/groups/{workspace_id}/users",
                headers=headers,
                data=body,
            )
            return response.status_code
        else:
            return 400

    def update_user_in_workspace(self, workspace_id: str, email: str, access: str = "Member") -> dict:
        """
        Updates the access level of a user in a workspace.

        Args:
            workspace_id (str): The ID of the workspace.
            email (str): The email address of the user to be updated.
            access (str, optional): The new access level for the user. Default is "Member".

        Returns:
            dict: A dictionary with the response code if the user was successfully updated, otherwise None.

        Raises:
            None
        """
        if not self.verify_token():
            return None

        if access in ["Admin", "Contributor", "Member"]:
            headers = {"Authorization": self.token["bearer"]}
            body = {"userEmailAddress": email, "groupUserAccessRight": access}
            response = requests.put(
                f"https://api.powerbi.com/v1.0/myorg/groups/{workspace_id}/users",
                headers=headers,
                data=body,
            )

            if response.status_code == 200:
                return {"response": response.status_code}
            else:
                log.error(
                    "Error %s -- Something went wrong when trying to update %s in the workspace %s",
                        response.status_code, email, workspace_id
                    )
                return None
        else:
            log.error(
                'Error 400 -- Please, make sure the access parameter is either "Admin", "Contributor" or "Member"'
            )
            return None

    # Report
    def get_reports(self, workspace_id: str) -> list:
        """
        Retrieves a list of reports in the specified workspace.

        Args:
            workspace_id (str): The ID of the workspace.

        Returns:
            list: A list of reports in the workspace if the retrieval was successful, otherwise None.

        Raises:
            None
        """
        if not self.verify_token():
            return None

        headers = {"Authorization": self.token["bearer"]}
        response = requests.get(
            f"https://api.powerbi.com/v1.0/myorg/groups/{workspace_id}/reports", headers=headers
        )

        if response.status_code == 200:
            return response.json()["value"]
        else:
            log.error(
                "Error %s -- Something went wrong when trying to retrieve the list of reports in the workspace %s",
                    response.status_code, workspace_id
                )
            return None

    def get_report(self, workspace_id: str, report_id: str) -> list:
        """
        Retrieves a specific report in the specified workspace.

        Args:
            workspace_id (str): The ID of the workspace.
            report_id (str): The ID of the report.

        Returns:
            list: The report if the retrieval was successful, otherwise None.

        Raises:
            None
        """
        if not self.verify_token():
            return None

        headers = {"Authorization": self.token["bearer"]}
        response = requests.get(
            f"https://api.powerbi.com/v1.0/myorg/groups/{workspace_id}/reports/{report_id}",
            headers=headers,
        )

        if response.status_code == 200:
            return response.json()
        else:
            log.error(
                "Error %s -- Something went wrong when trying to retrieve the report %s in the workspace %s",
                    response.status_code, report_id, workspace_id
                )
            return None

    def delete_report(self, workspace_id: str, report_id: str) -> dict:
        """
        Deletes a specific report in the specified workspace.

        Args:
            workspace_id (str): The ID of the workspace.
            report_id (str): The ID of the report.

        Returns:
            dict: A dictionary with the response code if the report was successfully deleted, otherwise None.

        Raises:
            None
        """
        if not self.verify_token():
            return None

        headers = {"Authorization": self.token["bearer"]}
        response = requests.delete(
            f"https://api.powerbi.com/v1.0/myorg/groups/{workspace_id}/reports/{report_id}",
            headers=headers,
        )

        if response.status_code == 200:
            return {"response": response.status_code}
        else:
            log.error(
                "Error %s -- Something went wrong when trying to delete the report %s in the workspace %s",
                    response.status_code, report_id, workspace_id
                )
            return None

    def export_report(self, workspace_id: str, report_id: str, out_file: str) -> dict:
        """
        Exports a specific report in the specified workspace.

        Args:
            workspace_id (str): The ID of the workspace.
            report_id (str): The ID of the report.
            out_file (str): The path and filename where the exported report will be saved.

        Returns:
            dict: A dictionary with the response code if the report was successfully exported, otherwise None.

        Raises:
            None
        """
        if not self.verify_token():
            return None

        headers = {"Authorization": self.token["bearer"]}
        response = requests.get(
            f"https://api.powerbi.com/v1.0/myorg/groups/{workspace_id}/reports/{report_id}/export",
            headers=headers,
        )

        if response.status_code == 200:
            with open(out_file, "wb") as file:
                file.write(response.content)
            return {"response": response.status_code}
        else:
            log.error(
                "Error %s -- Something went wrong when trying to export the report %s in the workspace %s",
                    response.status_code, report_id, workspace_id
            )
            return None

    def import_report(
        self,
        workspace_id: str,
        report_name: str,
        in_file: str,
        name_conflict: str = "CreateOrOverwrite",
    ) -> dict:
        """
        Imports a report file into the specified workspace.

        Args:
            workspace_id (str): The ID of the workspace.
            report_name (str): The display name for the imported report.
            in_file (str): The path and filename of the report file to import.
            name_conflict (str, optional): The conflict resolution strategy if a report with the same name already exists.
                                           Default is "CreateOrOverwrite".

        Returns:
            dict: A dictionary with the response code if the report was successfully imported, otherwise None.

        Raises:
            None
        """
        if not self.verify_token():
            return None

        if name_conflict in ["CreateOrOverwrite", "GenerateUniqueName", "Ignore", "Overwrite"]:
            headers = {"Authorization": self.token["bearer"], "Content-Type": "multipart/form-data"}
            file = {"file": open(in_file, "rb")}
            response = requests.post(
                f"https://api.powerbi.com/v1.0/myorg/groups/{workspace_id}/imports?\
                    datasetDisplayName={report_name}&nameConflict={name_conflict}",
                headers=headers,
                files=file,
            )

            if response.status_code == 202:
                return response.json()
            else:
                log.error(
                    "Error %s -- Something went wrong when trying to import the report %s in the workspace %s",
                        response.status_code, in_file, workspace_id
                    )
                return None
        else:
            log.error(
                'Error 400 -- Please, make sure the name_conflict parameter is either \
                    "CreateOrOverwrite", "GenerateUniqueName", "Ignore" or "Overwrite"'
            )
            return None

    def clone_report(
        self, workspace_id: str, report_id: str, dest_report_name: str, dest_workspace_id: str = None
    ) -> dict:
        """
        Clones a report in the specified workspace.

        Args:
            workspace_id (str): The ID of the source workspace.
            report_id (str): The ID of the report to clone.
            dest_report_name (str): The name to assign to the cloned report.
            dest_workspace_id (str, optional): The ID of the destination workspace. If not provided,
                                               the report will be cloned in the same workspace.

        Returns:
            dict: A dictionary with the response code if the report was successfully cloned, otherwise None.

        Raises:
            None
        """
        if not self.verify_token():
            return None

        headers = {"Authorization": self.token["bearer"]}
        if dest_workspace_id:
            body = {"name": dest_report_name, "targetWorkspaceId": dest_workspace_id}
        else:
            body = {"name": dest_report_name}

        response = requests.post(
            f"https://api.powerbi.com/v1.0/myorg/groups/{workspace_id}/reports/{report_id}/clone",
            headers=headers,
            data=body,
        )

        if response.status_code == 200:
            return {"response": response.status_code}
        else:
            log.error(
                "Error %s -- Something went wrong when trying to clone the report %s in the workspace %s",
                    response.status_code, report_id, workspace_id
                )
            return None

    # Dataset
    def get_datasets(self, workspace_id: str) -> list:
        """
        Retrieves a list of datasets in the specified workspace.

        Args:
            workspace_id (str): The ID of the workspace.

        Returns:
            list: A list of datasets in the workspace if the retrieval was successful, otherwise None.

        Raises:
            None
        """
        if not self.verify_token():
            return None

        headers = {"Authorization": self.token["bearer"]}
        response = requests.get(
            f"https://api.powerbi.com/v1.0/myorg/groups/{workspace_id}/datasets",
            headers=headers
        )

        if response.status_code == 200:
            return response.json()["value"]
        else:
            log.error(
                "Error %s -- Something went wrong when trying to retrieve the list of datasets in the workspace %s",
                    response.status_code, workspace_id
                )
            return None

    def get_dataset(self, workspace_id: str, dataset_id: str) -> list:
        """
        Retrieves a dataset in the specified workspace.

        Args:
            workspace_id (str): The ID of the workspace.
            dataset_id (str): The ID of the dataset.

        Returns:
            list: A list of datasets in the workspace if the retrieval was successful, otherwise None.

        Raises:
            None
        """
        if not self.verify_token():
            return None

        headers = {"Authorization": self.token["bearer"]}
        response = requests.get(
            f"https://api.powerbi.com/v1.0/myorg/groups/{workspace_id}/datasets/{dataset_id}",
            headers=headers,
        )

        if response.status_code == 200:
            return response.json()["value"]
        else:
            log.error(
                "Error %s -- Something went wrong when trying to retrieve the dataset %s in the workspace %s",
                    response.status_code, dataset_id, workspace_id
                )
            return None

    def get_dataset_users(self, workspace_id: str, dataset_id: str) -> list:
        """
        Retrieves dataset users in the specified workspace.

        Args:
            workspace_id (str): The ID of the workspace.
            dataset_id (str): The ID of the dataset.

        Returns:
            list: A list of dataset users in the workspace if the retrieval was successful, otherwise None.

        Raises:
            None
        """
        if not self.verify_token():
            return None

        headers = {"Authorization": self.token["bearer"]}
        response = requests.get(
            f"https://api.powerbi.com/v1.0/myorg/groups/{workspace_id}/datasets/{dataset_id}/users",
            headers=headers,
        )

        if response.status_code == 200:
            return response.json()
        else:
            log.error(
                "Error %s -- Something went wrong when trying to retrieve the users of dataset %s in the workspace %s",
                    response.status_code, dataset_id, workspace_id
                )
            return None

    def delete_dataset(self, workspace_id: str, dataset_id: str) -> dict:
        """
        Deletes a dataset in the specified workspace.

        Args:
            workspace_id (str): The ID of the workspace.
            dataset_id (str): The ID of the dataset.

        Returns:
            dict: A dictionary containing the response status code if successful, otherwise None.
        """
        if not self.verify_token():
            return None

        headers = {"Authorization": self.token["bearer"]}
        response = requests.delete(
            f"https://api.powerbi.com/v1.0/myorg/groups/{workspace_id}/datasets/{dataset_id}",
            headers=headers,
        )

        if response.status_code == 200:
            return {"response": response.status_code}
        else:
            log.error(
                "Error %s -- Something went wrong when trying to delete the dataset %s in the workspace %s",
                    response.status_code, dataset_id, workspace_id
                )
            return None

    def refresh_dataset(
        self, workspace_id: str, dataset_id: str, notify_option: str = "NoNotification"
    ) -> dict:
        """
        Refreshes a dataset in the specified workspace with the given notify option.

        Args:
            workspace_id (str): The ID of the workspace.
            dataset_id (str): The ID of the dataset.
            notify_option (str, optional): The notification option. Defaults to "NoNotification".

        Returns:
            dict: A dictionary containing the response status code if successful, otherwise None.
        """
        if not self.verify_token():
            return None
        headers = {"Authorization": self.token["bearer"]}
        body = {"notifyOption": notify_option}
        response = requests.post(
            f"https://api.powerbi.com/v1.0/myorg/groups/{workspace_id}/datasets/{dataset_id}/refreshes",
            headers=headers,
            data=body,
        )
        return response

    def make_api_call(self, endpoint: str, method: str, headers: dict = None, data: dict = None) -> dict:
        """
        Makes an API call with the specified parameters.

        Args:
            endpoint (str): The endpoint of the API to call (appended to the base URL).
            method (str): The HTTP method to use for the request (e.g., "GET", "POST").
            headers (dict, optional): A dictionary of headers to include in the request.
            data (dict, optional): A dictionary of data to include in the request body.

        Returns:
            dict: The JSON response from the API call, or None if there was an error.

        This function uses the `requests` library to make the API call with the specified method,
        headers, and data. The base URL (https://api.powerbi.com/) is prepended to the endpoint.
        It returns the JSON response from the API call as a dictionary if the request is successful.
        If there is an error during the request or authentication process, it logs an error and
        returns None.

        """
        if not self.verify_token():
            return None

        base_url = "https://api.powerbi.com/"
        url = base_url + endpoint

        headers = headers or {}
        headers["Authorization"] = self.token["bearer"]

        try:
            response = requests.request(method, url, headers=headers, json=data)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as ex:
            log.error("API call error: %s",ex)
            return None
