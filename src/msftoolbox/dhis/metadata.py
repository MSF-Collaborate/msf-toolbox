# dhis/src/dhis.py

import urllib.parse
import json
import requests

class dhis_metadata:
    def __init__(self, username=None, password=None, server_url=None):
        self.DHIS2_USERNAME = username
        self.DHIS2_PASSWORD = password
        self.DHIS2_SERVER_URL = server_url

    def configure_DHIS2_server(self, username=None, password=None, server_url=None):
        if username is not None:
            self.DHIS2_USERNAME = username
        if password is not None:
            self.DHIS2_PASSWORD = password
        if server_url is not None:
            self.DHIS2_SERVER_URL = server_url

    def getResponse(self, url):
        response = requests.get(url, auth=(self.DHIS2_USERNAME, self.DHIS2_PASSWORD))

        if response.status_code == 401:
            raise ValueError("Authentication failed. Check your username and password.")
        response.raise_for_status()

        data = response.json()
        return data

    def getOrgUnitChildren(self, uid):
        """
        Searches DHIS2 for all the direct children of an organization unit.
        :param uid: String of organization unit UID
        :return: List of (org unit child name, org unit child data sets))
        """
        url = f'{self.DHIS2_SERVER_URL}/api/organisationUnits/{uid}?includeChildren=true'
        data = self.getResponse(url)
        items = data['organisationUnits']
        children = [(item['name'], item['dataSets'], item['id']) for item in items if item['id'] != uid]

        return children

    def getDataSets(self, data_sets_uids):
        """
        Searches DHIS2 for every data set given in a list.
        :param data_sets_uids: List of data set objects retrieved from DHIS2
        :return: List of (data set name, data set id))
        """
        data_sets = []

        for uid_obj in data_sets_uids:
            uid = uid_obj['id']
            url = f'{self.DHIS2_SERVER_URL}/api/dataSets/{uid}'

            data = self.getResponse(url)
            data_set = (data['name'], data['id'], data['periodType'])
            data_sets.append(data_set)

        return data_sets