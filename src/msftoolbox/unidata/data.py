import requests
from urllib.error import HTTPError

class UniDataAPIClient:
    """
    A class to interact with the UniData API and manage data extraction.

    This class provides methods to configure the UniData server credentials, make authenticated
    requests to the server, and fetch specific data such as articles, subcatalogues, intros, and checklists.
    """

    def __init__(
        self,
        username:str,
        password:str,
        server_url:str,
        timeout=10
        ):
        """
        Initializes the UniDataAPIClient instance with optional UniData server credentials and URL.

        Args:
            username (str): UniData username.
            password (str): UniData password.
            server_url (str): UniData server URL.
            timeout (int, optional): Default timeout for requests in seconds. Defaults to 10.
        """
        self.username = username
        self.password = password
        self.server_url = server_url
        self.timeout = timeout

    def configure_unidata_server(
        self,
        username:str,
        password:str,
        server_url:str
        ):
        """
        Configures the UniData server credentials and URL.

        This method allows updating the UniData server username, password, and URL.

        Args:
            username (str): UniData username.
            password (str): UniData password.
            server_url (str): UniData server URL.
        """
        if username is not None:
            self.username = username
        if password is not None:
            self.password = password
        if server_url is not None:
            self.server_url = server_url

    def get_response(
        self,
        endpoint:str,
        params:dict=None,
        timeout:int=None
        ):
        """
        Makes an authenticated GET request to the specified endpoint and returns the JSON response.

        Args:
            endpoint (str): The API endpoint to send the GET request to.
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
        url = f'{self.server_url}{endpoint}'
        if params is None:
            params = {}
        params.update({'login': self.username, 'password': self.password})

        response = requests.get(url, params=params, timeout=timeout)
        if response.status_code == 401:
            raise HTTPError(
                response.url,
                response.status_code,
                "Authentication failed. Check your username and password.",
                response.headers,
                None
                )
        response.raise_for_status()

        return response.json()

    def get_articles(self, **kwargs):
        """
        Retrieves articles from the UniData API with optional query parameters.

        Args:
            **kwargs: Optional query parameters to filter the articles, including:
                - mode (int): Defines the level of details of the response. Default is 0.
                - formercode (str): A string of any requested current or former code.
                - filter (str): An XPath expression used to filter the table rows to retrieve.
                - links (int): Defines whether to include links in descriptions or labels.
                - publishonweb (bool): Defines the relevant Golden articles after validation.
                - size (int): The desired number of table rows per page. Default is 20.
                - page (int): The requested page number. Default is 1.

        Returns:
            dict: The articles data from the UniData API.
        """
        return self.get_response('/articles', params=kwargs)

    def get_subcatalogues(self):
        """
        Retrieves subcatalogues from the UniData API.

        Returns:
            dict: The subcatalogues data from the UniData API.
        """
        return self.get_response('/lists')

    def get_intros(self):
        """
        Retrieves intros from the UniData API.

        Returns:
            dict: The intros data from the UniData API.
        """
        return self.get_response('/intros')

    def get_checklists(self):
        """
        Retrieves checklists from the UniData API.

        Returns:
            dict: The checklists data from the UniData API.
        """
        return self.get_response('/checklists')