"""
Module to interact with the DHIS2 server and manage metadata and data values.
"""

import json
import requests


class DhisMetadata:
    """
    A class to interact with the DHIS2 server and retrieve metadata.

    This class provides methods to configure the DHIS2 server credentials, make authenticated
    requests to the server, and fetch specific metadata such as organization unit children
    and data sets.
    """

    def __init__(self, username=None, password=None, server_url=None, timeout=10):
        """
        Initializes the DhisMetadata instance with optional DHIS2 server credentials and URL.

        :param username: DHIS2 username (default: None)
        :param password: DHIS2 password (default: None)
        :param server_url: DHIS2 server URL (default: None)
        :param timeout: Default timeout for requests in seconds (default: 10)
        """
        self.dhis2_username = username
        self.dhis2_password = password
        self.dhis2_server_url = server_url
        self.timeout = timeout

    def configure_dhis2_server(self, username=None, password=None, server_url=None):
        """
        Configures the DHIS2 server credentials and URL.

        This method allows updating the DHIS2 server username, password, and URL.

        :param username: DHIS2 username (default: None)
        :param password: DHIS2 password (default: None)
        :param server_url: DHIS2 server URL (default: None)
        """
        if username is not None:
            self.dhis2_username = username
        if password is not None:
            self.dhis2_password = password
        if server_url is not None:
            self.dhis2_server_url = server_url

    def get_response(self, url, params=None, timeout=None):
        """
        Makes an authenticated GET request to the specified URL and returns the JSON response.

        :param url: The URL to send the GET request to.
        :param params: Optional query parameters to include in the request.
        :param timeout: Timeout for the request in seconds (default: instance's timeout).
        :return: The JSON response data.
        :raises ValueError: If authentication fails.
        :raises HTTPError: For other HTTP errors.
        """
        if timeout is None:
            timeout = self.timeout
        response = requests.get(
            url,
            auth=(self.dhis2_username, self.dhis2_password),
            params=params,
        )
        if response.status_code == 401:
            raise ValueError("Authentication failed. Check your username and password.")
        response.raise_for_status()

        return response.json()

    def get_all_org_units(self, **kwargs):
        """
        Retrieves all organization units from DHIS2 with optional query parameters.

        This method queries the DHIS2 API to fetch details of all organization units,
        supporting various query parameters to filter the results.

        :param kwargs: Optional query parameters to filter the organization units.
                       Supported parameters include:
                       - userOnly (bool)
                       - userDataViewOnly (bool)
                       - userDataViewFallback (bool)
                       - paging (bool) - turn to false to get more than 50 results
                       - query (str)
                       - level (int)
                       - maxLevel (int)
                       - withinUserHierarchy (bool)
                       - withinUserSearchHierarchy (bool)
                       - memberCollection (str)
                       - memberObject (str)
        :return: List of dictionaries, where each dictionary represents an organization unit.
        """
        url = f'{self.dhis2_server_url}/api/organisationUnits'
        params = {k: v for k, v in kwargs.items() if v is not None}
        data = self.get_response(url, params=params)
        return data['organisationUnits']

    def get_org_unit_children(self, uid):
        """
        Retrieves all direct children of a specified organization unit from DHIS2.

        This method queries the DHIS2 API to fetch details of all direct children of the given
        organization unit UID.

        :param uid: The UID of the organization unit.
        :return: List of dictionaries representing the child organization units.
        """
        url = f'{self.dhis2_server_url}/api/organisationUnits/{uid}?includeChildren=true'
        data = self.get_response(url)
        return data['organisationUnits']

    def get_data_sets_information(self, data_sets_uids):
        """
        Fetches data set details from DHIS2 for each data set UID provided.

        :param data_sets_uids: List of data set UIDs.
        :return: List of data set details.
        """
        data_sets = []

        for uid in data_sets_uids:
            url = f'{self.dhis2_server_url}/api/dataSets/{uid}'
            data = self.get_response(url)
            data_sets.append(data)

        return data_sets

    def get_indicators(self, **kwargs):
        """
        Retrieves all indicators from DHIS2.

        This method queries the DHIS2 API to fetch details of all indicators.

        :return: List of dictionaries, where each dictionary represents an indicator.
        """
        url = f'{self.dhis2_server_url}/api/indicators'
        params = {k: v for k, v in kwargs.items() if v is not None}
        data = self.get_response(url, params=params)
        return data['indicators']

    def get_data_elements(self, **kwargs):
        """
        Retrieves all data elements from DHIS2.

        This method queries the DHIS2 API to fetch details of all data elements.

        :return: List of dictionaries, where each dictionary represents a data element.
        """
        url = f'{self.dhis2_server_url}/api/dataElements'
        params = {k: v for k, v in kwargs.items() if v is not None}
        data = self.get_response(url, params=params)
        return data['dataElements']

    def get_data_elements_for_org_unit(self, org_unit_uid):
        """
        Retrieves all data elements for a specific organization unit from DHIS2.

        :param org_unit_uid: The UID of the organization unit.
        :return: List of dictionaries representing data elements.
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

        :return: List of dictionaries, where each dictionary represents a predictor.
        """
        url = f'{self.dhis2_server_url}/api/predictors'
        data = self.get_response(url)
        return data['predictors']

    def export_metadata(self, **kwargs):
        """
        Export metadata from the DHIS2 API.

        Parameters:
        - kwargs: Additional parameters to customize the metadata export.

        Returns:
        - response (dict): The JSON response from the API call.
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

class DhisDataValues:
    """
    A class to interact with the DHIS2 server and manage data values.

    This class provides methods to send, read, and delete data values in DHIS2.
    """

    def __init__(self, username=None, password=None, server_url=None, timeout=10):
        """
        Initializes the DhisDataValues instance with optional DHIS2 server credentials and URL.

        :param username: DHIS2 username (default: None)
        :param password: DHIS2 password (default: None)
        :param server_url: DHIS2 server URL (default: None)
        :param timeout: Default timeout for requests in seconds (default: 10)
        """
        self.dhis2_username = username
        self.dhis2_password = password
        self.dhis2_server_url = server_url
        self.timeout = timeout

    def configure_dhis2_server(self, username=None, password=None, server_url=None):
        """
        Configures the DHIS2 server credentials and URL.

        This method allows updating the DHIS2 server username, password, and URL.

        :param username: DHIS2 username (default: None)
        :param password: DHIS2 password (default: None)
        :param server_url: DHIS2 server URL (default: None)
        """
        if username is not None:
            self.dhis2_username = username
        if password is not None:
            self.dhis2_password = password
        if server_url is not None:
            self.dhis2_server_url = server_url

    def send_data_values(self, data_values, content_type='json', **kwargs):
        """
        Sends data values to the DHIS2 server.

        :param data_values: The data values to send. This can be a dictionary for JSON,
                            XML string, or CSV string.
        :param content_type: The content type of the data values ('json', 'xml', or 'csv').
        :param kwargs: Additional query parameters for the request.
        :return: The response from the DHIS2 server.
        """
        url = f'{self.dhis2_server_url}/api/dataValueSets'
        headers = {'Content-Type': f'application/{content_type}'}
        params = {k: v for k, v in kwargs.items() if v is not None}

        if content_type == 'json':
            data = json.dumps(data_values)
        else:
            data = data_values

        response = requests.post(
            url,
            auth=(self.dhis2_username, self.dhis2_password),
            headers=headers,
            params=params,
            data=data,
        )
        response.raise_for_status()
        return response.json()

    def read_data_values(self, **kwargs):
        """
        Reads data values from the DHIS2 server.

        :param kwargs: Query parameters for the request.
        :return: The data values from the DHIS2 server.
        """
        url = f'{self.dhis2_server_url}/api/dataValueSets'
        params = {k: v for k, v in kwargs.items() if v is not None}

        response = requests.get(
            url,
            auth=(self.dhis2_username, self.dhis2_password),
            params=params,
        )
        response.raise_for_status()
        return response.json()

    def delete_data_value(
        self, data_element, period, org_unit, category_option_combo=None, attribute_option_combo=None
    ):
        """
        Deletes a data value from the DHIS2 server.

        :param data_element: The data element identifier.
        :param period: The period identifier.
        :param org_unit: The organization unit identifier.
        :param category_option_combo: The category option combo identifier (optional).
        :param attribute_option_combo: The attribute option combo identifier (optional).
        :return: The response from the DHIS2 server.
        """
        url = f'{self.dhis2_server_url}/api/dataValues'
        params = {
            'de': data_element,
            'pe': period,
            'ou': org_unit,
            'co': category_option_combo,
            'cc': attribute_option_combo,
        }

        response = requests.delete(
            url,
            auth=(self.dhis2_username, self.dhis2_password),
            params=params,
        )
        response.raise_for_status()
        return response.json()

    def send_individual_data_value(self, data_value):
        """
        Sends an individual data value to the DHIS2 server.

        :param data_value: The data value to send. This should be a dictionary.
        :return: The response from the DHIS2 server.
        """
        url = f'{self.dhis2_server_url}/api/dataValues'
        headers = {'Content-Type': 'application/json'}
        data = json.dumps(data_value)

        response = requests.post(
            url,
            auth=(self.dhis2_username, self.dhis2_password),
            headers=headers,
            data=data,
        )
        response.raise_for_status()
        return response.json()

    def read_individual_data_value(
        self, data_element, period, org_unit, category_option_combo=None, attribute_option_combo=None
    ):
        """
        Reads an individual data value from the DHIS2 server.

        :param data_element: The data element identifier.
        :param period: The period identifier.
        :param org_unit: The organization unit identifier.
        :param category_option_combo: The category option combo identifier (optional).
        :param attribute_option_combo: The attribute option combo identifier (optional).
        :return: The data value from the DHIS2 server.
        """
        url = f'{self.dhis2_server_url}/api/dataValues'
        params = {
            'de': data_element,
            'pe': period,
            'ou': org_unit,
            'co': category_option_combo,
            'cc': attribute_option_combo,
        }

        response = requests.get(
            url,
            auth=(self.dhis2_username, self.dhis2_password),
            params=params,
        )
        response.raise_for_status()
        return response.json()
