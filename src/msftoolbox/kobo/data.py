import requests


class KoboClient:
    """A class to interact with the Kobo API and extract data from specific assets/surveys."""

    def __init__(self, base_url, api_token):
        """
        Initialize the KoboClient with an API token for authentication.
        API token can be obtained from Kobo interface: Account Settings/Security/API key

        Args:
            base_url (str): The base URL of the Kobo API.
            api_token (str): The API token for token-based authentication.
        """
        self.base_url = base_url
        self.params = {
            "format": "json"
        }
        self.headers = {
            'Authorization': f'Token {api_token}'
        }

        # Run authentication check on init
        self.auth_status = self._check_auth()

        if not self.auth_status["Authenticated"]:
            msg = (
                f"Authentication failed. "
                f"Status: {self.auth_status.get('Status_code')}, "
                f"Error: {self.auth_status.get('Error')}"
            )
            raise RuntimeError(msg)
        print("Authentication succeeded")

    def _check_auth(self):
        # Check authentication by checking access to assets
        url = f"{self.base_url}/assets/"
        try:
            response = requests.get(url, headers=self.headers, params=self.params)
            if response.status_code == 200:
                return {
                    "Authenticated": True,
                    "Status_code": response.status_code
                }
            else:
                return {
                    "Authenticated": False,
                    "Status_code": response.status_code,
                    "Error": response.text
                }
        except requests.exceptions.RequestException as e:
            return {
                "Authenticated": False,
                "Error": str(e)
            }

    def list_assets(self):
        """
        Retrieve a list of all assets/surveys from the Kobo API, available for this user.

        Returns:
            list: A list of asset dictionaries obtained from the API.

        Raises:
            requests.exceptions.HTTPError: If an HTTP error occurs during the request.
        """
        url = f'{self.base_url}assets/'
        response = requests.get(url, params=self.params, headers=self.headers)

        if response.status_code == 200:
            response_json = response.json()
            return response_json['results']
        else:
            response.raise_for_status()

    def get_asset_uid(self, asset_name):
        """
        Get the asset UID based on the asset name.

        Args:
            asset_name (str): The name of the asset to look up.

        Returns:
            str: The UID of the asset if found.

        Raises:
            ValueError: If the asset name is not found in the results.
        """
        try:
            assets = self.list_assets()

            # Loop through each item in the list of assets
            for item in assets:
                # Check if the current item's name matches the asset_name
                if item.get('name') == asset_name:
                    # Return the UID if a match is found
                    return item.get('uid')

            # If no match is found, raise a ValueError
            raise ValueError(f"Asset name '{asset_name}' not found.")

        except requests.exceptions.HTTPError as e:
            # Handle HTTP errors if needed
            raise e

    def get_asset(self, asset_uid):
        """
        Retrieve a specific asset/survey from the Kobo API.

        Args:
            asset_uid (str): The unique identifier of the asset.

        Returns:
            dict: A dictionary representing the asset.

        Raises:
            requests.exceptions.HTTPError: If an HTTP error occurs during the request.
        """
        url = f'{self.base_url}assets/{asset_uid}'
        response = requests.get(url, params=self.params, headers=self.headers)

        if response.status_code == 200:
            response_json = response.json()
            return response_json
        else:
            response.raise_for_status()

    def get_asset_data(self, asset_uid):
        """
        Retrieve all data for a specific Kobo asset/survey, handling pagination.

        Args:
            asset_uid (str): The unique identifier of the asset to retrieve data from.

        Returns:
            list: A list of dictionaries with all results retrieved from the asset, across all pages.

        Raises:
            requests.exceptions.HTTPError: If an HTTP error occurs during the request.
        """
        all_results = []
        url = f'{self.base_url}assets/{asset_uid}/data/'

        while url:
            response = requests.get(url, params=self.params, headers=self.headers)
            if response.status_code == 200:
                data = response.json()
                all_results.extend(data['results'])
                url = data.get('next')  # Get the next page URL
            else:
                response.raise_for_status()

        return all_results

    def get_asset_metadata(self, asset_uid):
        """
        Extracts labels and related metadata from a specified asset.

        This method retrieves the asset structure from an asset identified by its unique ID
        and extracts relevant information such as the group, name, type, and labels of each survey item.

        Args:
            asset_uid (str): The unique identifier of the asset to retrieve data from.

        Returns:
            list of dict
                A list of dictionaries where each dictionary contains the following keys:
                - 'group': The group name extracted from the item's XPath, or None if not applicable.
                - 'name': The name of the survey item.
                - 'type': The type of the survey item.
                - 'label': A list of labels associated with the survey item.

        Notes:
        -----
        - The method assumes that the asset dictionary contains a 'content' key with a 'survey' key,
        which is a list of survey item dictionaries.
        - The XPath is used to determine the group and repeat information
        """
        asset_dict = self.get_asset(asset_uid)
        survey_items = asset_dict['content']['survey']

        extracted_data = []

        for item in survey_items:
            item_type = item.get('type')

            # Extract group from $xpath
            xpath = item.get('$xpath', '')
            path_parts = xpath.split('/')

            # Determine the  group based on the path parts
            group = None

            if len(path_parts) > 1:
                # Check if the first part is a repeat by examining its type
                if any(part.startswith('RPT') for part in path_parts):
                    group = path_parts[1] if len(path_parts) > 2 else None
                else:
                    group = path_parts[0]

            # Extract the necessary fields
            name = item.get('name')
            label = item.get('label', [])
            required = item.get('required', None)
            hint = item.get('hint', None)

            # Create a dictionary with the extracted data
            data_entry = {
                'type': item_type,
                'group': group,
                'name': name,
                'label': label,
                'hint': hint,
                'required': required,
                'question_code': xpath
            }
            extracted_data.append(data_entry)

        return extracted_data

    def get_asset_choice_items(self, asset_uid):
        """
        This function retrieves the choice items from an asset dictionary
        and extracts relevant information such as the name and label (multiple languages, if applicable)

        Args:
            asset_uid (str): The unique identifier of the asset to retrieve data from.

        Returns:
            list of dict
                A list of dictionaries where each dictionary contains the following keys:
                - 'list_name': The name of the list this choice item belongs to
                - 'name': The name of the item.
                - 'label': A list of labels associated with the answers

        Notes:
        -----
        - The method assumes that the asset dictionary contains a 'content' key with a 'choices' key,
        which is a list of choice item dictionaries.

            """
        asset_dict = self.get_asset(asset_uid)
        choice_items = asset_dict['content']['choices']
        extracted_data = []

        for item in choice_items:
            # Extract the necessary fields
            list_name = item.get('list_name')
            name = item.get('name')
            label = item.get('label', [])

            # Create a dictionary with the extracted data
            data_entry = {
                'list_name': list_name,
                'name': name,
                'label': label
            }
            extracted_data.append(data_entry)

        return extracted_data
