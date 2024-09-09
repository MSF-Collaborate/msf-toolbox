# dhis/src/dhis.py

import urllib.parse
import json
import requests

import requests

class DhisMetadata:
    """
    A class to interact with the DHIS2 server and retrieve metadata.

    This class provides methods to configure the DHIS2 server credentials, make authenticated
    requests to the server, and fetch specific metadata such as organization unit children and data sets.
    """

    def __init__(self, username=None, password=None, server_url=None):
        """
        Initializes the DhisMetadata instance with optional DHIS2 server credentials and URL.

        :param username: DHIS2 username (default: None)
        :param password: DHIS2 password (default: None)
        :param server_url: DHIS2 server URL (default: None)
        """
        self.dhis2_username = username
        self.dhis2_password = password
        self.dhis2_server_url = server_url

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

    def get_response(self, url):
        """
        Makes an authenticated GET request to the specified URL and returns the JSON response.

        :param url: The URL to send the GET request to.
        :return: The JSON response data.
        :raises ValueError: If authentication fails.
        :raises HTTPError: For other HTTP errors.
        """
        response = requests.get(url, auth=(self.dhis2_username, self.dhis2_password))

        if response.status_code == 401:
            raise ValueError("Authentication failed. Check your username and password.")
        response.raise_for_status()

        return response.json()

    def get_all_org_units(self, **kwargs):
        """
        Retrieves all organization units from DHIS2 with optional query parameters.

        This method queries the DHIS2 API to fetch details of all organization units, supporting
        various query parameters to filter the results.

        :param kwargs: Optional query parameters to filter the organization units.
                       Supported parameters include:
                       - userOnly (bool)
                       - userDataViewOnly (bool)
                       - userDataViewFallback (bool)
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
        :return: List of tuples, where each tuple contains:
                 - child organization unit name (str)
                 - child organization unit data sets (list)
                 - child organization unit ID (str)
        """
        url = f'{self.dhis2_server_url}/api/organisationUnits/{uid}?includeChildren=true'
        data = self.get_response(url)
        items = data['organisationUnits']
        children = [(item['name'], item['dataSets'], item['id']) for item in items if item['id'] != uid]
        return children

    def get_data_sets_information(self, data_sets_uids):
        """
        Fetches data set details from DHIS2 for each data set UID provided.

        This function takes a list of data set UID objects, queries the DHIS2 API for each UID,
        and retrieves the corresponding data set details. It returns a list of tuples containing
        the data set name, data set ID, and period type.

        :param data_sets_uids: List of dictionaries, where each dictionary contains the 'id' key 
                            representing the UID of a data set.
        :return: List of tuples, where each tuple contains:
                - data set name (str)
                - data set ID (str)
                - period type (str)
        """
        data_sets = []

        for uid_obj in data_sets_uids:
            uid = uid_obj['id']
            url = f'{self.dhis2_server_url}/api/dataSets/{uid}'
            data = self.get_response(url)
            data_set = (data['name'], data['id'], data['periodType'])
            data_sets.append(data_set)

        return data_sets

    def get_indicators(self):
        """
        Retrieves all indicators from DHIS2.

        This method queries the DHIS2 API to fetch details of all indicators.

        :return: List of dictionaries, where each dictionary represents an indicator.
        """
        url = f'{self.dhis2_server_url}/api/indicators'
        data = self.get_response(url)
        return data['indicators']

    def get_data_elements(self):
        """
        Retrieves all data elements from DHIS2.

        This method queries the DHIS2 API to fetch details of all data elements.

        :return: List of dictionaries, where each dictionary represents a data element.
        """
        url = f'{self.dhis2_server_url}/api/dataElements'
        data = self.get_response(url)
        return data['dataElements']

    def get_data_elements_for_org_unit(self, org_unit_uid):
        """
        Retrieves all data elements for a specific organization unit from DHIS2.

        This method queries the DHIS2 API to fetch details of all data elements associated with 
        the data sets linked to the given organization unit UID.

        :param org_unit_uid: The UID of the organization unit.
        :return: List of dictionaries, where each dictionary represents a data element.
        """
        # Step 1: Fetch data sets for the organization unit
        url = f'{self.dhis2_server_url}/api/organisationUnits/{org_unit_uid}?fields=dataSets'
        data = self.get_response(url)
        data_sets = data.get('dataSets', [])

        # Step 2: Fetch data elements for each data set
        data_elements = []
        for data_set in data_sets:
            data_set_id = data_set['id']
            url = f'{self.dhis2_server_url}/api/dataSets/{data_set_id}?fields=dataSetElements[dataElement]'
            data_set_data = self.get_response(url)
            data_set_elements = data_set_data.get('dataSetElements', [])

            for element in data_set_elements:
                data_element = element['dataElement']
                data_elements.append(data_element)

        return data_elements