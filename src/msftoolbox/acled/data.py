import requests
from datetime import datetime

class ACLEDClient:
    """A class to interact with the ACLED API, allowing data extraction and filtering."""

    BASE_URL = "https://api.acleddata.com"

    def __init__(self, api_key: str, email: str, limit: int = 50, format: str = "json"):
        """Initializes the ACLED Extractor.

        Args:
            api_key (str): The API key for authentication.
            email (str): The email associated with the API key.
            limit (int, optional): Number of results to return. Defaults to 50.
            format (str, optional): Format of the returned data. Defaults to "json".
        """
        self.api_key = api_key
        self.email = email
        self.limit = limit
        self.format = format

    def get_response(self, api_url: str, params: dict, get_data: bool = True):
        """Makes a GET request to the specified API endpoint with the given parameters.

        Args:
            api_url (str): The API endpoint path.
            params (dict): The query parameters for the request.
            get_data (bool): Whether to return only the 'data' field or the entire response.

        Returns:
            dict or list: The data from the API response.
        """
        full_url = f"{self.BASE_URL}{api_url}"
        response = requests.get(full_url, params=params)

        if response.status_code != 200:
            raise requests.HTTPError(f"Error: {response.status_code}, {response.text}")

        if get_data:
            return response.json().get("data", [])
        else:
            return response.json()

    def list_events(self, **kwargs) -> list:
        """Lists events from the ACLED API with optional filters.

        Keyword Args:
            data_id (int): Filter by data ID.
            iso (int): Filter by ISO country code.
            event_id_cnty (str): Filter by event ID country.
            event_id_no_cnty (str): Filter by event ID without country.
            event_date (str): Filter by event date in YYYY-MM-DD format. It can also be between dates then format is "YYYY-MM-DD|YYYY-MM-DD" and toggle event_date_where=BETWEEN
            year (int): Filter by year.
            time_precision (int): Filter by time precision.
            event_type (str): Filter by event type.
            sub_event_type (str): Filter by sub-event type.
            actor1 (str): Filter by primary actor.
            assoc_actor_1 (str): Filter by associated actor 1.
            inter1 (int): Filter by interaction 1.
            actor2 (str): Filter by secondary actor.
            assoc_actor_2 (str): Filter by associated actor 2.
            inter2 (int): Filter by interaction 2.
            interaction (int): Filter by interaction.
            region (int): Filter by region.
            country (str): Filter by country name.

        Returns:
            list: A list of events matching the filters.
        """
        api_url = "/acled/read"
        params = {
            "key": self.api_key,
            "email": self.email,
            "limit": self.limit,
            "format": self.format
        }

        # Add additional query parameters from kwargs
        params.update(kwargs)

        return self.get_response(api_url, params)

    def list_actors(self, **kwargs) -> list:
        """Lists actors from the ACLED API with optional filters.

        Keyword Args:
            actor_name (str): Filter by actor name.
            first_event_date (str): Filter by the first event date in YYYY-MM-DD format.
            last_event_date (str): Filter by the last event date in YYYY-MM-DD format.
            event_count (int): Filter by the number of events.

        Returns:
            list: A list of actors matching the filters.
        """
        api_url = "/actor/read"
        params = {
            "key": self.api_key,
            "email": self.email,
            "limit": kwargs.get("limit", self.limit),
            "format": self.format
        }

        params.update(kwargs)

        return self.get_response(api_url, params)

    def list_regions(self, **kwargs) -> list:
        """Lists regions from the ACLED API with optional filters.

        Keyword Args:
            region (int): Filter by region ID.
            region_name (str): Filter by region name.
            first_event_date (str): Filter by the first event date in YYYY-MM-DD format.
            last_event_date (str): Filter by the last event date in YYYY-MM-DD format.

        Returns:
            list: A list of regions matching the filters.
        """
        api_url = "/region/read"
        params = {
            "key": self.api_key,
            "email": self.email,
            "limit": kwargs.get("limit", self.limit),
            "format": self.format
        }

        params.update(kwargs)

        return self.get_response(api_url, params)

    def list_countries(self, **kwargs) -> list:
        """Lists countries from the ACLED API with optional filters.

        Keyword Args:
            country (str): Filter by country name.
            iso (int): Filter by ISO country code.
            first_event_date (str): Filter by the first event date in YYYY-MM-DD format.
            last_event_date (str): Filter by the last event date in YYYY-MM-DD format.

        Returns:
            list: A list of countries matching the filters.
        """
        api_url = "/country/read"
        params = {
            "key": self.api_key,
            "email": self.email,
            "limit": kwargs.get("limit", self.limit),
            "format": self.format
        }

        params.update(kwargs)

        return self.get_response(api_url, params)