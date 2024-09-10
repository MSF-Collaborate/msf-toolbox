# dhis/src/module.py
import json
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

    def get_response(self, url, params=None):
        """
        Makes an authenticated GET request to the specified URL and returns the JSON response.

        :param url: The URL to send the GET request to.
        :param params: Optional query parameters to include in the request.
        :return: The JSON response data.
        :raises ValueError: If authentication fails.
        :raises HTTPError: For other HTTP errors.
        """
        response = requests.get(url, auth=(self.dhis2_username, self.dhis2_password), params=params)
        
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
        - kwargs: Additional parameters to customize the metadata export. Examples include:
            - fields (str): Default field filter to apply for all types (e.g., 'id,displayName').
            - filter (str): Default object filter to apply for all types (e.g., 'name:^like:ANC').
            - order (str): Default order to apply to all types (e.g., 'displayName:desc').
            - translate (str): Enable translations ('false' or 'true').
            - locale (str): Change from user locale to a custom locale (e.g., 'en').
            - defaults (str): Include or exclude auto-generated category objects ('INCLUDE' or 'EXCLUDE').
            - skipSharing (str): Strip sharing properties from exported objects ('false' or 'true').
            - download (str): Handle data as an attachment ('false' or 'true').
            - indicators (str): Include indicators in the export ('true' or 'false').
            - indicatorGroups (str): Include indicator groups in the export ('true' or 'false').
            - dataElements (str): Include data elements in the export ('true' or 'false').
            - dataElements__fields (str): Fields to include for data elements (e.g., 'id,displayName').
            - dataElements__order (str): Order to apply for data elements (e.g., 'displayName:desc').

        Returns:
        - response (dict): The JSON response from the API call.

        Example usage:
        - Export all metadata ordered by lastUpdated descending:
          export_metadata(defaultOrder='lastUpdated:desc')
        
        - Export metadata only including indicators and indicator groups:
          export_metadata(indicators='true', indicatorGroups='true')
        
        - Export id and displayName for all data elements, ordered by displayName:
          export_metadata(dataElements='true', dataElements__fields='id,displayName', dataElements__order='displayName:desc')
        
        - Export data elements and indicators where name starts with "ANC":
          export_metadata(filter='name:^like:ANC', dataElements='true', indicators='true')
        """
        endpoint = '/api/metadata'
        url = f"{self.dhis2_server_url}{endpoint}"

        # Prepare the query parameters
        params = {k: v for k, v in kwargs.items() if v is not None}

        # Make the GET request to the API
        response = requests.get(url, auth=(self.dhis2_username, self.dhis2_password), params=params)

        # Check if the request was successful
        if response.status_code == 200:
            return response.json()  # Return the JSON response
        else:
            response.raise_for_status()  # Raise an exception for HTTP errors

class DhisDataValues:
    """
    A class to interact with the DHIS2 server and manage data values.

    This class provides methods to send, read, and delete data values in DHIS2.
    """

    def __init__(self, username=None, password=None, server_url=None):
        """
        Initializes the DhisDataValues instance with optional DHIS2 server credentials and URL.

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

    def send_data_values(self, data_values, content_type='json', **kwargs):
        """
        Sends data values to the DHIS2 server.

        :param data_values: The data values to send. This can be a dictionary for JSON, XML string, or CSV string.
        :param content_type: The content type of the data values ('json', 'xml', or 'csv').
        :param kwargs: Additional query parameters for the request. Examples include:
                       - dataElementIdScheme (str): Property of the data element object to use to map the data values.
                       - orgUnitIdScheme (str): Property of the org unit object to use to map the data values.
                       - attributeOptionComboIdScheme (str): Property of the attribute option combo object to use to map the data values.
                       - categoryOptionComboIdScheme (str): Property of the category option combo object to use to map the data values.
                       - dataSetIdScheme (str): Property of the data set object to use to map the data values.
                       - preheatCache (bool): Indicates whether to preload metadata caches before starting to import data values.
                       - dryRun (bool): Whether to save changes on the server or just return the import summary.
                       - importStrategy (str): Save objects of all, new or update import status on the server.
                       - skipExistingCheck (bool): Skip checks for existing data values. Improves performance.
                       - skipAudit (bool): Skip audit, meaning audit values will not be generated.
                       - async (bool): Indicates whether the import should be done asynchronous or synchronous.
                       - force (bool): Indicates whether the import should be forced.

        :return: The response from the DHIS2 server.

        Example usage:
        - Send data values in JSON format with dryRun:
          send_data_values(data_values_json, content_type='json', dryRun=True)
        
        - Send data values in XML format with preheatCache:
          send_data_values(data_values_xml, content_type='xml', preheatCache=True)

        - Send data values in CSV format:
          send_data_values(data_values_csv, content_type='csv')
        """
        url = f'{self.dhis2_server_url}/api/dataValueSets'
        headers = {'Content-Type': f'application/{content_type}'}
        params = {k: v for k, v in kwargs.items() if v is not None}

        if content_type == 'json':
            data = json.dumps(data_values)
        else:
            data = data_values  # Assuming data_values is a string containing XML or CSV

        response = requests.post(url, auth=(self.dhis2_username, self.dhis2_password), headers=headers, params=params, data=data)
        response.raise_for_status()
        return response.json()

    def read_data_values(self, **kwargs):
        """
        Reads data values from the DHIS2 server.

        :param kwargs: Query parameters for the request. Examples include:
                       - dataSet (str): Data set identifier.
                       - period (str): Period identifier in ISO format.
                       - orgUnit (str): Organisation unit identifier.
                       - startDate (str): Start date for the time span of the values to export.
                       - endDate (str): End date for the time span of the values to export.
                       - children (bool): Whether to include the children in the hierarchy of the organisation units.
                       - lastUpdated (str): Include only data values which are updated since the given time stamp.
                       - limit (int): The max number of results in the response.
                       - includeDeleted (bool): Whether to include deleted data values.

        :return: The data values from the DHIS2 server.

        Example usage:
        - Read data values for a specific data set and period:
          read_data_values(dataSet='pBOMPrpg1QX', period='201401', orgUnit='DiszpKrYNg8')

        - Read data values updated in the last 10 days:
          read_data_values(dataSet='pBOMPrpg1QX', orgUnit='DiszpKrYNg8', lastUpdatedDuration='10d')
        """
        url = f'{self.dhis2_server_url}/api/dataValueSets'
        params = {k: v for k, v in kwargs.items() if v is not None}

        response = requests.get(url, auth=(self.dhis2_username, self.dhis2_password), params=params)
        response.raise_for_status()
        return response.json()

    def delete_data_value(self, data_element, period, org_unit, category_option_combo=None, attribute_option_combo=None):
        """
        Deletes a data value from the DHIS2 server.

        :param data_element: The data element identifier.
        :param period: The period identifier.
        :param org_unit: The organization unit identifier.
        :param category_option_combo: The category option combo identifier (optional).
        :param attribute_option_combo: The attribute option combo identifier (optional).
        :return: The response from the DHIS2 server.

        Example usage:
        - Delete a specific data value:
          delete_data_value(data_element='f7n9E0hX8qk', period='201401', org_unit='DiszpKrYNg8')
        """
        url = f'{self.dhis2_server_url}/api/dataValues'
        params = {
            'de': data_element,
            'pe': period,
            'ou': org_unit,
            'co': category_option_combo,
            'cc': attribute_option_combo
        }

        response = requests.delete(url, auth=(self.dhis2_username, self.dhis2_password), params=params)
        response.raise_for_status()
        return response.json()

    def send_individual_data_value(self, data_value):
        """
        Sends an individual data value to the DHIS2 server.

        :param data_value: The data value to send. This should be a dictionary.
        :return: The response from the DHIS2 server.

        Example usage:
        - Send an individual data value:
          individual_data_value = {
              "dataElement": "fbfJHSPpUQD",
              "categoryOptionCombo": "PT59n8BQbqM",
              "period": "202201",
              "orgUnit": "DiszpKrYNg8",
              "value": "10",
              "comment": "OK"
          }
          send_individual_data_value(individual_data_value)
        """
        url = f'{self.dhis2_server_url}/api/dataValues'
        headers = {'Content-Type': 'application/json'}
        data = json.dumps(data_value)

        response = requests.post(url, auth=(self.dhis2_username, self.dhis2_password), headers=headers, data=data)
        response.raise_for_status()
        return response.json()

    def read_individual_data_value(self, data_element, period, org_unit, category_option_combo=None, attribute_option_combo=None):
        """
        Reads an individual data value from the DHIS2 server.

        :param data_element: The data element identifier.
        :param period: The period identifier.
        :param org_unit: The organization unit identifier.
        :param category_option_combo: The category option combo identifier (optional).
        :param attribute_option_combo: The attribute option combo identifier (optional).
        :return: The data value from the DHIS2 server.

        Example usage:
        - Read an individual data value:
          read_individual_data_value(data_element='fbfJHSPpUQD', period='202201', org_unit='DiszpKrYNg8')
        """
        url = f'{self.dhis2_server_url}/api/dataValues'
        params = {
            'de': data_element,
            'pe': period,
            'ou': org_unit,
            'co': category_option_combo,
            'cc': attribute_option_combo
        }

        response = requests.get(url, auth=(self.dhis2_username, self.dhis2_password), params=params)
        response.raise_for_status()
        return response.json()