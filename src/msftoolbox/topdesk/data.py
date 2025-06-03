import requests
from datetime import datetime
from uuid import UUID

class TopDeskIncidentClient:
    """
    A client to interact with the TopDesk Incident API.

    This class provides methods to manage incidents, including retrieval, creation, escalation, and more.
    """

    def __init__(self, topdesk_url: str, username: str, password: str):
        """
        Initialize the TopDeskIncidentClient with the URL and credentials.

        Args:
            topdesk_url (str): The base URL for the TopDesk API.
            username (str): The username for authentication.
            password (str): The password for authentication.
        """
        self.topdesk_url = topdesk_url.rstrip("/")
        self.auth = (username, password)

    def request_topdesk(self, endpoint: str, method: str = "GET", params: dict = None, data: dict = None) -> dict:
        """
        Make a request to the TopDesk API.

        Args:
            endpoint (str): The API endpoint.
            method (str): The HTTP method (GET, POST, PUT, DELETE). Defaults to "GET".
            params (dict, optional): URL parameters. Defaults to None.
            data (dict, optional): JSON data for POST/PUT requests. Defaults to None.

        Returns:
            dict: The JSON response from the API.
        """
        url = f"{self.topdesk_url}{endpoint}"
        response = requests.request(method, url, auth=self.auth, params=params, json=data)
        response.raise_for_status()
        if response.status_code == 204:
            return {}
        return response.json()

    def is_valid_uuid(self, value: str) -> bool:
        """
        Check if a string is a valid UUID.

        Args:
            value (str): The string to check.

        Returns:
            bool: True if valid UUID, False otherwise.
        """
        try:
            UUID(value, version=4)
            return True
        except ValueError:
            return False

    def _incident_endpoint(self, incident_id: str, suffix: str = "") -> str:
        """
        Build an endpoint path for a given incident ID or number.

        Args:
            incident_id (str): The UUID or number of the incident.
            suffix (str): An optional suffix for further path components.

        Returns:
            str: The formatted endpoint.
        """
        path = "id" if self.is_valid_uuid(incident_id) else "number"
        return f"/tas/api/incidents/{path}/{incident_id}{suffix}"

    def list_incidents(
        self, 
        fiql_query: str = None,
        offset: int = 0,  # Use offset instead of page_start
        page_size: int = 10, 
        sort: str = "creationDate:desc", 
        fields: str = None, 
        date_format: str = "iso8601", 
        **kwargs
    ) -> list:
        """
        List incidents with optional filtering by FIQL query, pagination, sorting, and field selection.

        Args:
            fiql_query (str, optional): A FIQL query string for filtering incidents. Defaults to None.
            offset (int, optional): The starting point for incidents retrieval, used for paging. Defaults to 0.
            page_size (int, optional): The number of incidents to retrieve per page. Defaults to 10.
            sort (str, optional): The sorting order of incidents, e.g., "creationDate:desc". Defaults to "creationDate:desc".
            fields (str, optional): A comma-separated list of fields to include in the response. Defaults to None.
            date_format (str, optional): The format of date fields in the response. Defaults to "iso8601".
            **kwargs: Additional query parameters to include in the request.

        Returns:
            list: A list of incidents matching the query parameters.
        """
        params = {
            'pageSize': page_size,
            'start': offset,  # Use offset for paging
            'sort': sort,
            'dateFormat': date_format,
            **kwargs
        }
        if fields:
            params['fields'] = fields
        if fiql_query:
            params['query'] = fiql_query
        return self.request_topdesk("/tas/api/incidents", params=params)

    def get_incident(self, incident_id: str) -> dict:
        """
        Retrieve an incident by its ID or number.
        """
        endpoint = self._incident_endpoint(incident_id)
        return self.request_topdesk(endpoint)


    def get_incident_actions(self, incident_id: str, **kwargs) -> dict:
        """
        Get actions associated with an incident.

        Only includes non-falsy query parameters to avoid invalid requests.

        Args:
            incident_id (str): UUID or number of the incident.
            **kwargs: Optional query parameters (e.g., start, page_size, inlineimages, etc.)

        Returns:
            dict: API response.
        """
        endpoint = self._incident_endpoint(incident_id, "/actions")
        params = {k: v for k, v in kwargs.items() if v not in [None, False, 0]}
        return self.request_topdesk(endpoint, params=params)

    def get_incident_request(self, incident_id: str, **kwargs) -> dict:
        """
        Get a specific request related to an incident.

        Only includes non-falsy query parameters to avoid invalid requests.

        Args:
            incident_id (str): UUID of the incident.
            **kwargs: Optional query parameters (e.g., inlineimages, etc.)

        Returns:
            dict: API response.
        """
        endpoint = f"/tas/api/incidents/id/{incident_id}/requests"
        params = {k: v for k, v in kwargs.items() if v not in [None, False, 0]}
        return self.request_topdesk(endpoint, params=params)
