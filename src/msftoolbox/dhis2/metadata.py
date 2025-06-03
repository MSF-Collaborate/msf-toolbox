"""
Module to interact with the DHIS2 server and manage metadata and data values.
"""

import requests
from requests.auth import HTTPBasicAuth

class Dhis2MetadataClient:
    """
    A class to interact with the DHIS2 server and retrieve metadata.

    This class provides methods to configure the DHIS2 server credentials, make authenticated
    requests to the server, and fetch specific metadata such as organization unit children
    and data sets.
    """

    def __init__(self, username=None, password=None, server_url=None, personal_access_token=None, timeout=10):
        """
        Initializes the DhisMetadata instance with optional DHIS2 server credentials and URL.

        Args:
            username (str, optional): DHIS2 username. Defaults to None.
            password (str, optional): DHIS2 password. Defaults to None.
            personal_access_token (str, optional): DHIS2 personal access token. Defaults to None
            server_url (str, optional): DHIS2 server URL. Defaults to None.
            timeout (int, optional): Default timeout for requests in seconds. Defaults to 10.
        """
        self.dhis2_username = username
        self.dhis2_password = password
        self.dhis2_personal_access_token = personal_access_token
        self.dhis2_server_url = server_url
        self.timeout = timeout

    def get_response(self, url, params=None, timeout=None):
        """
        Makes an authenticated GET request to the specified URL and returns the JSON response.

        Args:
            url (str): The URL to send the GET request to.
            params (dict, optional): Optional query parameters to include in the request.
            timeout (int, optional): Timeout for the request in seconds. Defaults to instance's timeout.

        Returns:
            dict: The JSON response data.

        Raises:
            ValueError: If authentication fails.
            HTTPError: For other HTTP errors.
        """
        if timeout is None:
            timeout = self.timeout

        headers = {}
        auth = None

        if self.dhis2_personal_access_token:
            headers['Authorization'] = f'ApiToken {self.dhis2_personal_access_token}'
        elif self.dhis2_username and self.dhis2_password:
            auth = HTTPBasicAuth(self.dhis2_username, self.dhis2_password)
        else:
            raise ValueError("Authentication credentials are not provided. Please provide a username and password or a personal access token.")

        response = requests.get(
            url,
            auth=auth,
            headers=headers,
            params=params,
            timeout=timeout
        )
        
        if response.status_code == 401:
            raise ValueError("Authentication failed. Check your username and password.")
        response.raise_for_status()

        return response.json()

    def get_organisation_units(self, **kwargs):
        """
        Retrieves all organization units from DHIS2 with optional query parameters.

        This method queries the DHIS2 API to fetch details of all organization units,
        supporting various query parameters to filter the results.

        Args:
            **kwargs: Optional query parameters to filter the organization units.
                      Supported parameters include:
                          userOnly (bool)
                          userDataViewOnly (bool)
                          userDataViewFallback (bool)
                          paging (bool)     turn to false to get more than 50 results
                          query (str)
                          level (int)
                          maxLevel (int)
                          withinUserHierarchy (bool)
                          withinUserSearchHierarchy (bool)
                          memberCollection (str)
                          memberObject (str)

        Returns:
            list: List of dictionaries, where each dictionary represents an organization unit.
        """
        url = f'{self.dhis2_server_url}/api/organisationUnits'
        params = {k: v for k, v in kwargs.items() if v is not None}
        data = self.get_response(url, params=params)
        return data['organisationUnits']

    def add_organisation_unit_name_path(
        self,
        organisation_units
        ):
        """
        Converts the org unit id path to a path of names based on the `path` field in the organisation unit

        Args:
            organisation_units (list): The list of org unit dictionaries from the get_organisation_units method.

        Returns:
            list: The list of dictionaries with an additional key organisation_unit_name_path.
        """
        all_organisation_units = self.get_organisation_units(
            paging=False,
            fields="id,name"
            )

        mapper = {
            record["id"]: record["name"] for record in all_organisation_units
        }

        for record in organisation_units:
            temp_parts = record["path"].strip('/').split('/')

            # Replace each part with its corresponding name from the mapping
            replaced_parts = [mapper.get(part, part) for part in temp_parts]

            # Join the parts back into a path
            record["organisation_unit_name_path"] = ' > '.join(replaced_parts)

        return organisation_units


    def get_org_unit_children(self, uid):
        """
        Retrieves all direct children of a specified organization unit from DHIS2.

        This method queries the DHIS2 API to fetch details of all direct children of the given
        organization unit UID.

        Args:
            uid (str): The UID of the organization unit.

        Returns:
            list: List of dictionaries representing the child organization units.
        """
        url = f'{self.dhis2_server_url}/api/organisationUnits/{uid}?includeChildren=true'
        data = self.get_response(url)
        return data['organisationUnits']

    def get_datasets(self, **kwargs):
        """
        Retrieves all datasets from DHIS2.

        This method queries the DHIS2 API to fetch details of all datasets.

        Args:
            **kwargs: Optional query parameters to filter the datasets.

        Returns:
            list: List of dictionaries, where each dictionary represents an dataset.
        """
        url = f'{self.dhis2_server_url}/api/dataSets'
        params = {k: v for k, v in kwargs.items() if v is not None}
        data = self.get_response(url, params=params)
        return data['dataSets']

    def get_programs(self, **kwargs):
        """
        Retrieves all programs from DHIS2.

        This method queries the DHIS2 API to fetch details of all programs.

        Args:
            **kwargs: Optional query parameters to filter the programs.

        Returns:
            list: List of dictionaries, where each dictionary represents a program.
        """
        url = f'{self.dhis2_server_url}/api/programs'
        params = {k: v for k, v in kwargs.items() if v is not None}
        data = self.get_response(url, params=params)
        return data['programs']

    def get_program_stages(self, **kwargs):
        """
        Retrieves all program stages from DHIS2.

        This method queries the DHIS2 API to fetch details of all program stages.

        Args:
            **kwargs: Optional query parameters to filter the program stages.

        Returns:
            list: List of dictionaries, where each dictionary represents a program stage.
        """
        url = f'{self.dhis2_server_url}/api/programStages'
        params = {k: v for k, v in kwargs.items() if v is not None}
        data = self.get_response(url, params=params)
        return data['programStages']

    def get_program_rules(self, **kwargs):
        """
        Retrieves all program stages from DHIS2.

        This method queries the DHIS2 API to fetch details of all program stages.

        Args:
            **kwargs: Optional query parameters to filter the program stages.

        Returns:
            list: List of dictionaries, where each dictionary represents a program stage.
        """
        url = f'{self.dhis2_server_url}/api/programRules'
        params = {k: v for k, v in kwargs.items() if v is not None}
        data = self.get_response(url, params=params)
        return data['programRules']

    def get_indicators(self, **kwargs):
        """
        Retrieves all indicators from DHIS2.

        This method queries the DHIS2 API to fetch details of all indicators.

        Args:
            **kwargs: Optional query parameters to filter the indicators.

        Returns:
            list: List of dictionaries, where each dictionary represents an indicator.
        """
        url = f'{self.dhis2_server_url}/api/indicators'
        params = {k: v for k, v in kwargs.items() if v is not None}
        data = self.get_response(url, params=params)
        return data['indicators']

    def get_indicator_groups(self, **kwargs):
        """
        Retrieves all indicators from DHIS2.

        This method queries the DHIS2 API to fetch details of all indicators.

        Args:
            **kwargs: Optional query parameters to filter the indicators.

        Returns:
            list: List of dictionaries, where each dictionary represents an indicator.
        """
        url = f'{self.dhis2_server_url}/api/indicatorGroups'
        params = {k: v for k, v in kwargs.items() if v is not None}
        data = self.get_response(url, params=params)
        return data['indicatorGroups']

    def get_program_indicators(self, **kwargs):
        """
        Retrieves all program indicators from DHIS2.

        This method queries the DHIS2 API to fetch details of all program indicators.

        Args:
            **kwargs: Optional query parameters to filter the program indicators.

        Returns:
            list: List of dictionaries, where each dictionary represents a program indicator.
        """
        url = f'{self.dhis2_server_url}/api/programIndicators'
        params = {k: v for k, v in kwargs.items() if v is not None}
        data = self.get_response(url, params=params)
        return data['programIndicators']

    def get_program_indicator_groups(self, **kwargs):
        """
        Retrieves all program indicator groups from DHIS2.

        This method queries the DHIS2 API to fetch details of all program indicator groups.

        Args:
            **kwargs: Optional query parameters to filter the program indicator groups.

        Returns:
            list: List of dictionaries, where each dictionary represents a program indicator group.
        """
        url = f'{self.dhis2_server_url}/api/programIndicatorGroups'
        params = {k: v for k, v in kwargs.items() if v is not None}
        data = self.get_response(url, params=params)
        return data['programIndicatorGroups']

    def get_data_elements(self, **kwargs):
        """
        Retrieves all data elements from DHIS2.

        This method queries the DHIS2 API to fetch details of all data elements.

        Args:
            **kwargs: Optional query parameters to filter the data elements.

        Returns:
            list: List of dictionaries, where each dictionary represents a data element.
        """
        url = f'{self.dhis2_server_url}/api/dataElements'
        params = {k: v for k, v in kwargs.items() if v is not None}
        data = self.get_response(url, params=params)
        return data['dataElements']


    def get_data_element_groups(self, **kwargs):
        """
        Retrieves all data element groups from DHIS2.

        This method queries the DHIS2 API to fetch details of all data element groups.

        Args:
            **kwargs: Optional query parameters to filter the data element groups.

        Returns:
            list: List of dictionaries, where each dictionary represents a data element group.
        """
        url = f'{self.dhis2_server_url}/api/dataElementGroups'
        params = {k: v for k, v in kwargs.items() if v is not None}
        data = self.get_response(url, params=params)
        return data['dataElementGroups']

    def get_option_sets(self, **kwargs):
        """
        Retrieves all option sets from DHIS2.

        This method queries the DHIS2 API to fetch details of all option sets.

        Args:
            **kwargs: Optional query parameters to filter the option sets.

        Returns:
            list: List of dictionaries, where each dictionary represents an option set.
        """
        url = f'{self.dhis2_server_url}/api/optionSets'
        params = {k: v for k, v in kwargs.items() if v is not None}
        data = self.get_response(url, params=params)
        return data['optionSets']

    def get_options(self, **kwargs):
        """
        Retrieves all options from DHIS2.

        This method queries the DHIS2 API to fetch details of all options.

        Args:
            **kwargs: Optional query parameters to filter the options.

        Returns:
            list: List of dictionaries, where each dictionary represents a option.
        """
        url = f'{self.dhis2_server_url}/api/options'
        params = {k: v for k, v in kwargs.items() if v is not None}
        data = self.get_response(url, params=params)
        return data['options']

    def get_data_elements_for_org_unit(self, org_unit_uid):
        """
        Retrieves all data elements for a specific organization unit from DHIS2.

        Args:
            org_unit_uid (str): The UID of the organization unit.

        Returns:
            list: List of dictionaries representing data elements.
        """
        url = f'{self.dhis2_server_url}/api/organisationUnits/{org_unit_uid}?fields=dataSets'
        data = self.get_response(url)
        data_sets = data.get('dataSets', [])

        data_elements = []
        for data_set in data_sets:
            data_set_id = data_set['id']
            url = (
                f'{self.dhis2_server_url}/api/dataSets/{data_set_id}?fields=dataSetElements[dataElement]'
            )
            data_set_data = self.get_response(url)
            data_set_elements = data_set_data.get('dataSetElements', [])

            for element in data_set_elements:
                data_element = element['dataElement']
                data_elements.append(data_element)

        return data_elements

    def get_predictors(self):
        """
        Retrieves all predictors from DHIS2.

        This method queries the DHIS2 API to fetch details of all predictors.

        Returns:
            list: List of dictionaries, where each dictionary represents a predictor.
        """
        url = f'{self.dhis2_server_url}/api/predictors'
        data = self.get_response(url)
        return data['predictors']

    def export_metadata(self, **kwargs):
        """
        Export metadata from the DHIS2 API.

        Args:
            **kwargs: Additional parameters to customize the metadata export.

        Returns:
            dict: The JSON response from the API call.

        Raises:
            ValueError: If the response status code is not 200.
        """
        endpoint = '/api/metadata'
        url = f"{self.dhis2_server_url}{endpoint}"

        params = {k: v for k, v in kwargs.items() if v is not None}

        response = requests.get(
            url,
            auth=(self.dhis2_username, self.dhis2_password),
            params=params,
        )

        response.raise_for_status()
        if response.status_code == 200:
            return response.json()
        else:
            raise ValueError(
                f'Expected `200` http status response code, received: {response.status_code}'
            )
