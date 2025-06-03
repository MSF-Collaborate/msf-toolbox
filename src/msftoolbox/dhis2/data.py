"""
Module to interact with the DHIS2 server and manage metadata and data values.
"""

import json
import requests
from requests.auth import HTTPBasicAuth

class Dhis2DataValuesClient:
    """
    A class to interact with the DHIS2 server and manage data values.

    This class provides methods to send, read, and delete data values in DHIS2.
    """

    def __init__(self, username=None, password=None, server_url=None, personal_access_token=None, timeout=10):
        """
        Initializes the DhisDataValues instance with optional DHIS2 server credentials and URL.

        Args:
            username (str, optional): DHIS2 username. Defaults to None.
            password (str, optional): DHIS2 password. Defaults to None.
            server_url (str, optional): DHIS2 server URL. Defaults to None.
            timeout (int, optional): Default timeout for requests in seconds. Defaults to 10.
        """
        self.dhis2_username = username
        self.dhis2_password = password
        self.dhis2_server_url = server_url
        self.dhis2_personal_access_token = personal_access_token
        self.timeout = timeout

    def send_data_values(self, data_values, content_type='json', **kwargs):
        """
        Sends data values to the DHIS2 server.

        Args:
            data_values (dict or str): The data values to send. This can be a dictionary for JSON,
                                       XML string, or CSV string.
            content_type (str, optional): The content type of the data values ('json', 'xml', or 'csv').
                                          Defaults to 'json'.
            **kwargs: Additional query parameters for the request.

        Returns:
            dict: The response from the DHIS2 server.
        """
        url = f'{self.dhis2_server_url}/api/dataValueSets'
        headers = {'Content-Type': f'application/{content_type}'}
        params = {k: v for k, v in kwargs.items() if v is not None}

        if content_type == 'json':
            data = json.dumps(data_values)
        else:
            data = data_values

        timeout = self.timeout
        auth = None

        if self.dhis2_personal_access_token:
            headers['Authorization'] = f'ApiToken {self.dhis2_personal_access_token}'
        elif self.dhis2_username and self.dhis2_password:
            auth = HTTPBasicAuth(self.dhis2_username, self.dhis2_password)
        else:
            raise ValueError("Authentication credentials are not provided. Please provide a username and password or a personal access token.")

        response = requests.post(
            url,
            auth=auth,
            headers=headers,
            params=params,
            data=data,
            timeout=timeout
        )
        
        response.raise_for_status()
        return response.json()

    def read_data_values(self, **kwargs):
        """
        Reads data values from the DHIS2 server.

        Args:
            **kwargs: Query parameters for the request.

        Returns:
            dict: The data values from the DHIS2 server.
        """
        url = f'{self.dhis2_server_url}/api/dataValueSets'
        params = {k: v for k, v in kwargs.items() if v is not None}

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
        response.raise_for_status()
        return response.json()

    def delete_data_value(self, data_element, period, org_unit, category_option_combo=None, attribute_option_combo=None):
        """
        Deletes a data value from the DHIS2 server.

        Args:
            data_element (str): The data element identifier.
            period (str): The period identifier.
            org_unit (str): The organization unit identifier.
            category_option_combo (str, optional): The category option combo identifier. Defaults to None.
            attribute_option_combo (str, optional): The attribute option combo identifier. Defaults to None.

        Returns:
            dict: The response from the DHIS2 server.
        """
        url = f'{self.dhis2_server_url}/api/dataValues'
        params = {
            'de': data_element,
            'pe': period,
            'ou': org_unit,
            'co': category_option_combo,
            'cc': attribute_option_combo,
        }

        timeout = self.timeout

        headers = {}
        auth = None

        if self.dhis2_personal_access_token:
            headers['Authorization'] = f'ApiToken {self.dhis2_personal_access_token}'
        elif self.dhis2_username and self.dhis2_password:
            auth = HTTPBasicAuth(self.dhis2_username, self.dhis2_password)
        else:
            raise ValueError("Authentication credentials are not provided. Please provide a username and password or a personal access token.")

        response = requests.delete(
            url,
            auth=auth,
            headers=headers,
            params=params,
            timeout=timeout
        )

        response.raise_for_status()
        return response.json()

    def send_individual_data_value(self, data_value):
        """
        Sends an individual data value to the DHIS2 server.

        Args:
            data_value (dict): The data value to send. This should be a dictionary.

        Returns:
            dict: The response from the DHIS2 server.
        """
        url = f'{self.dhis2_server_url}/api/dataValues'
        headers = {'Content-Type': 'application/json'}
        data = json.dumps(data_value)

        timeout = self.timeout
        auth = None

        if self.dhis2_personal_access_token:
            headers['Authorization'] = f'ApiToken {self.dhis2_personal_access_token}'
        elif self.dhis2_username and self.dhis2_password:
            auth = HTTPBasicAuth(self.dhis2_username, self.dhis2_password)
        else:
            raise ValueError("Authentication credentials are not provided. Please provide a username and password or a personal access token.")

        response = requests.post(
            url,
            auth=auth,
            headers=headers,
            data=data,
            timeout=timeout
        )
        response.raise_for_status()
        return response.json()

    def read_individual_data_value(self, data_element, period, org_unit, category_option_combo=None, attribute_option_combo=None):
        """
        Reads an individual data value from the DHIS2 server.

        Args:
            data_element (str): The data element identifier.
            period (str): The period identifier.
            org_unit (str): The organization unit identifier.
            category_option_combo (str, optional): The category option combo identifier. Defaults to None.
            attribute_option_combo (str, optional): The attribute option combo identifier. Defaults to None.

        Returns:
            dict: The data value from the DHIS2 server.
        """
        url = f'{self.dhis2_server_url}/api/dataValues'
        params = {
            'de': data_element,
            'pe': period,
            'ou': org_unit,
            'co': category_option_combo,
            'cc': attribute_option_combo,
        }

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

        response.raise_for_status()
        return response.json()