from typing import Optional

import requests
import datetime
import logging
import json
from zipfile import ZipFile
import shutil
import pandas as pd

log = logging.getLogger()


class PowerBI:
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
            "https://login.microsoftonline.com/{}/oauth2/token".format(self.tenant_id),
            headers=headers,
            data=body,
        )

        if response.status_code == 200:
            self.set_token(response.json()["access_token"])
            log.info("Connected to the Power BI REST API with {}".format(self.username))
        else:
            self.token["bearer"] = None
            self.token["expiration"] = None
            log.error(
                "Error {} -- Something went wrong when trying to retrieve the token from the REST API".format(
                    response.status_code
                )
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
        self.token["bearer"] = "Bearer {}".format(bearer)
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
            ws = [result for result in response.json()["value"] if result["id"] == workspace_id]
            if len(ws) > 0:
                return ws[0]
            else:
                return None
        else:
            log.error(
                "Error {} -- Something went wrong when trying to retrieve the workspace {}".format(
                    response.status_code, workspace_id
                )
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
                "Error {} -- Something went wrong when trying to retrieve the list of workspaces you have access".format(
                    response.status_code
                )
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
            "https://api.powerbi.com/v1.0/myorg/groups/{}/users".format(workspace_id), headers=headers
        )

        if response.status_code == 200:
            return response.json()
        else:
            log.error(
                "Error {} -- Something went wrong when trying to retrieve the list of users in the workspace {}".format(
                    response.status_code, workspace_id
                )
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
                "https://api.powerbi.com/v1.0/myorg/groups/{}/users".format(workspace_id),
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
                "https://api.powerbi.com/v1.0/myorg/groups/{}/users".format(workspace_id),
                headers=headers,
                data=body,
            )

            if response.status_code == 200:
                return {"response": response.status_code}
            else:
                log.error(
                    "Error {} -- Something went wrong when trying to update {} in the workspace {}".format(
                        response.status_code, email, workspace_id
                    )
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
            "https://api.powerbi.com/v1.0/myorg/groups/{}/reports".format(workspace_id), headers=headers
        )

        if response.status_code == 200:
            return response.json()["value"]
        else:
            log.error(
                "Error {} -- Something went wrong when trying to retrieve the list of reports in the workspace {}".format(
                    response.status_code, workspace_id
                )
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
            "https://api.powerbi.com/v1.0/myorg/groups/{}/reports/{}".format(workspace_id, report_id),
            headers=headers,
        )

        if response.status_code == 200:
            return response.json()
        else:
            log.error(
                "Error {} -- Something went wrong when trying to retrieve the report {} in the workspace {}".format(
                    response.status_code, report_id, workspace_id
                )
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
            "https://api.powerbi.com/v1.0/myorg/groups/{}/reports/{}".format(workspace_id, report_id),
            headers=headers,
        )

        if response.status_code == 200:
            return {"response": response.status_code}
        else:
            log.error(
                "Error {} -- Something went wrong when trying to delete the report {} in the workspace {}".format(
                    response.status_code, report_id, workspace_id
                )
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
            "https://api.powerbi.com/v1.0/myorg/groups/{}/reports/{}/export".format(workspace_id, report_id),
            headers=headers,
        )

        if response.status_code == 200:
            with open(out_file, "wb") as file:
                file.write(response.content)
            return {"response": response.status_code}
        else:
            log.error(
                "Error {} -- Something went wrong when trying to export the report {} in the workspace {}".format(
                    response.status_code, report_id, workspace_id
                )
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
            name_conflict (str, optional): The conflict resolution strategy if a report with the same name already exists. Default is "CreateOrOverwrite".

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
                "https://api.powerbi.com/v1.0/myorg/groups/{}/imports?datasetDisplayName={}&nameConflict={}".format(
                    workspace_id, report_name, name_conflict
                ),
                headers=headers,
                files=file,
            )

            if response.status_code == 202:
                return response.json()
            else:
                log.error(
                    "Error {} -- Something went wrong when trying to import the report {} in the workspace {}".format(
                        response.status_code, in_file, workspace_id
                    )
                )
                return None
        else:
            log.error(
                'Error 400 -- Please, make sure the name_conflict parameter is either "CreateOrOverwrite", "GenerateUniqueName", "Ignore" or "Overwrite"'
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
            dest_workspace_id (str, optional): The ID of the destination workspace. If not provided, the report will be cloned in the same workspace.

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
            "https://api.powerbi.com/v1.0/myorg/groups/{}/reports/{}/clone".format(workspace_id, report_id),
            headers=headers,
            data=body,
        )

        if response.status_code == 200:
            return {"response": response.status_code}
        else:
            log.error(
                "Error {} -- Something went wrong when trying to clone the report {} in the workspace {}".format(
                    response.status_code, report_id, workspace_id
                )
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
            "https://api.powerbi.com/v1.0/myorg/groups/{}/datasets".format(workspace_id), headers=headers
        )

        if response.status_code == 200:
            return response.json()["value"]
        else:
            log.error(
                "Error {} -- Something went wrong when trying to retrieve the list of datasets in the workspace {}".format(
                    response.status_code, workspace_id
                )
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
            "https://api.powerbi.com/v1.0/myorg/groups/{}/datasets/{}".format(workspace_id, dataset_id),
            headers=headers,
        )

        if response.status_code == 200:
            return response.json()["value"]
        else:
            log.error(
                "Error {} -- Something went wrong when trying to retrieve the dataset {} in the workspace {}".format(
                    response.status_code, dataset_id, workspace_id
                )
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
            "https://api.powerbi.com/v1.0/myorg/groups/{}/datasets/{}/users".format(workspace_id, dataset_id),
            headers=headers,
        )

        if response.status_code == 200:
            return response.json()
        else:
            log.error(
                "Error {} -- Something went wrong when trying to retrieve the users of dataset {} in the workspace {}".format(
                    response.status_code, dataset_id, workspace_id
                )
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
            "https://api.powerbi.com/v1.0/myorg/groups/{}/datasets/{}".format(workspace_id, dataset_id),
            headers=headers,
        )

        if response.status_code == 200:
            return {"response": response.status_code}
        else:
            log.error(
                "Error {} -- Something went wrong when trying to delete the dataset {} in the workspace {}".format(
                    response.status_code, dataset_id, workspace_id
                )
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
            "https://api.powerbi.com/v1.0/myorg/groups/{}/datasets/{}/refreshes".format(
                workspace_id, dataset_id
            ),
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
        except requests.exceptions.RequestException as e:
            log.error("API call error: {}".format(e))
            return None


class ReportExtractor:
    """
    A class to extract information from Power BI report files.

    This class provides methods to extract measures, columns, and aggregations from a Power BI report
    file (with a .pbix extension). It reads the report's internal JSON configuration and extracts
    relevant information.

    Attributes:
        path (str): The path where the report files are located.
        name (str): The name of the report file with .pbix extension.
        result (list): A list to store the extracted information.
    """

    def __init__(self, path, name):
        """
        Initializes the ReportExtractor class.

        Args:
            path (str): The path where the report files are located.
            name (str): The name of the report file with pbix extension.
        """
        self.path = path
        self.name = name
        self.result = []

    def extract(self):
        """
        Extracts information from the report file.

        This function extracts information from a report file in a specific format.
        The report file is a ZIP archive containing layout and configuration files.

        The function performs the following steps:
        1. Create a temporary folder based on the report name.
        2. Extract the contents of the report file to the temporary folder.
        3. Load the report layout from the extracted files.
        4. Iterate over the sections of the report layout and extract information from each visual container.
        5. Store the extracted information in a list of fields.
        6. Remove the temporary folder.

        Returns:
            None
        """
        pathFolder = f"{self.path}/temp_{self.name[:-5]}"
        try:
            shutil.rmtree(pathFolder)
        except FileNotFoundError:
            print(f"folder {pathFolder} not present")
        with ZipFile(f"{self.path}/{self.name}", "r") as f:
            f.extractall(pathFolder)

        with open(f"{pathFolder}/Report/Layout", "r", encoding="utf-16 le") as reportFile:
            report_layout = json.loads(
                reportFile.read()
            )

        fields = []
        for s in report_layout["sections"]:
            for vc in s["visualContainers"]:
                try:
                    query_dict = json.loads(vc["config"])
                    for command in query_dict["singleVisual"]["prototypeQuery"]["Select"]:
                        if "Measure" in command.keys():
                            # - MEASURES
                            name = command["Name"].split(".")[1]
                            table = command["Name"].split(".")[0]
                            fields.append([s["displayName"], query_dict["name"], table, name, "Measure"])

                        elif "Column" in command.keys():
                            # COLUMNS
                            name = command["Name"].split(".")[1]
                            table = command["Name"].split(".")[0]
                            fields.append([s["displayName"], query_dict["name"], table, name, "Column"])

                        elif "Aggregation" in command.keys():
                            # AGGREGATIONS
                            if ("(" in command["Name"]) & (")" in command["Name"]):
                                txt_extraction = command["Name"][
                                    command["Name"].find("(") + 1 : command["Name"].find(")")
                                ]
                                name = txt_extraction.split(".")[1]
                                table = txt_extraction.split(".")[0]
                                fields.append(
                                    [s["displayName"], query_dict["name"], table, name, "Aggregation"]
                                )

                except (KeyError, json.JSONDecodeError):
                    pass
        self.result = fields
        shutil.rmtree(pathFolder)
