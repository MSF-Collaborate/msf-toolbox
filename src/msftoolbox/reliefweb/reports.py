import requests
import pandas as pd
from datetime import datetime, timedelta

class ReliefWebExtractor():
    """A class that allows to list reports from the Relief Web Updates API,
    loop over the reports and store them to a datalake

    Args:
        BaseELT (BaseELT): The BaseClass for our ELT platform
    """
    def __init__(
        self,
        app_name = "testing-rwapi",
        preset = "latest",
        limit = 50,
        profile = "full"
        ):
        """Initialises the Relief Web Extractor

        Args:
            process_stage (str): The stage of the pipeline
            source_type (str): The source of the data
            destination_type (str): The destination of the data
            datalake_url (str): The URL of the storage account.
            datalake_container_name (str): The name of the container in the storage account.
            app_name (str, optional): The name of the app. Required by Relief Web for their analytics. Defaults to "testing-rwapi".
            preset (str, optional): A shorthand specification of sets of fields, filters and sort order for common use-cases.
                                    Defaults to "latest", which sorts by date for appropriate content types. Countries and sources sorted by id. .
            limit (int, optional): How many results to return. Defaults to 1000, max 1000.
            profile (str, optional): A shorthand specification for which sets of fields to include in result.. Defaults to "full".
        """
        self.app_name = app_name
        self.preset = preset
        self.limit = limit
        self.profile = profile

    def try_key(
        self,
        key:str,
        data:dict
        ):
        """Tests a key in a dictionary and resolves to None if missing

        Args:
            key (str): They key to test for
            data (dict): The dictionary to test in

        Returns:
            any: The value associated with the key
        """
        if key in data.keys():
            return data[key]
        else:
            print(f"Key {key} missing in article {data['title']}")
            return None

    def validate_date(
        self,
        date_string:str
        ) -> bool:
        """Returns a boolean indicating if the date string is in "%Y-%m-%d" format

        Args:
            date_string (str): The date as a string

        Returns:
            bool: True is a correctly formatted string and False is a wrongly formatted string
        """
        try:
            # Try to create a datetime object from the date_str
            # This checks both the format and the validity of the date (e.g., no February 30)
            datetime.strptime(date_string, "%Y-%m-%d")
            return True
        except ValueError:
            # If ValueError is raised, the format is wrong or the date is invalid
            return False


    def list_reports(
        self,
        start_date:str,
        end_date:str,
        query_value:str,
        query_fields:list = ["body", "title"],
        query_operator:str = "OR",
        country_filter:list = None,
        response_format:str = "dictionary"
        ) -> list:
        """List all reports matching a query with optional filters.

        Args:
            start_date (str): The start date in YYYY-MM-DD format.
            end_date (str): The end date in YYYY-MM-DD format.
            query_value (str): The value to search for. This is equivalent to what would be entered in the Relief Web search bar.
            query_fields (list): The fields to search in. Allowed values can be found at: https://apidoc.reliefweb.int/fields-tables.
            query_operator (str): The operator ('OR', 'AND') determining how to treat queries with multiple search keywords.
            country_filter (list): A list of ISO3 country codes for filtering. ISO3 codes can be found at: https://www.iban.com/country-codes.
            response_format (str): The response format, either "dictionary" or "dataframe".

        Returns:
            list: A list of reports from the response.json()["data"].

        Raises:
            ValueError: If invalid values are provided for query_operator, response_format, or date format.
            HttpError: If the HTTP request returns a status code other than 200.
        """

        if query_operator not in ["OR", "AND"]:
            raise ValueError( f"Value {query_operator} not allowed for query_operator. Allowed values are: OR, AND")

        if response_format not in ["dataframe", "dictionary"]:
            raise ValueError( f"Value {response_format} not allowed for response_format. Allowed values are: dictionary, dataframe")

        if self.validate_date(start_date) and self.validate_date(end_date):
            all_filters = {
                "operator": "AND",
                "conditions": [{
                    "field": "date.original",
                    "value": {
                        "from": f"{start_date}T00:00:00+00:00",
                        "to": f"{end_date}T23:59:59+00:00"
                        }
                    }
                ]
            }
        else:
            raise ValueError(f"Invalid date: {start_date} or {end_date}. \
                Dates must be in YYYY-MM-DD format.")

        if country_filter is not None:
            all_filters["conditions"] .append(
                    {
                    "field": "country.iso3",
                    "value": country_filter,
                    "operator": "OR"
                    }
                )
        base_url = f"https://api.reliefweb.int/v1/reports?appname={self.app_name}"

        # set the request headers and body
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json"  # set the accept header to "application/json"
        }

        payload = {
            "preset": self.preset,
            "limit": self.limit,
            "query": {
                "value": query_value,
                "fields": query_fields,
                "operator": query_operator
            },
            "filter": all_filters,
            "fields":{"include":["source.name", "date", "language.name"]}
        }

        # Send request to URL
        response = requests.post(
            base_url,
            headers=headers,
            json=payload
            )


        if response.status_code != 200:
            raise requests.HTTPError(
                f"We have an error with status code: {response.status_code} \
                and text: {response.text}"
            )

        if response_format == "dictionary":
            response_data = response.json()["data"]
            records = [
                {
                    "id": record["id"],
                    "title": record["fields"]["title"],
                    "title_english": record["fields"]["title"],
                    "source_name": " / ".join([source['name'] for source in record["fields"]["source"]]),
                    "language": " / ".join([language['name'] for language in record["fields"]["language"]]),
                    "date": record["fields"]["date"]["original"],
                    "url": record["href"]
                } for record in response_data
            ]
            return records
        else:
            return pd.DataFrame(response.json()["data"])


    def get_report(
        self,
        report_url:str
        ) -> dict:
        """Get a report based on the report url.

        Args:
            report_url (str): The url for the report. Typically the href the list_reports response

        Returns:
            dict: A dictionary containing keys the full report information.
        """
        profile = self.profile
        base_url = f"{report_url}?appname={self.app_name}&profile={profile}"

        # Send request to URL
        response = requests.get(
            base_url
            )

        if response.status_code != 200:
            raise requests.HTTPError(
                f"We have an error with status code: {response.status_code} \
                and text: {response.text}"
            )

        return response.json()["data"]

    def parse_report_data(
        self,
        report_data:dict
        ) -> dict:
        """Returns a subset of fields. The ID of the report, the title, the status, \
        the body, the original link and the url.

        Args:
            report_data (dict): The response from get_report

        Returns:
            dict: A dictionary containing keys id, title, status, \
             origin_url, source_url and country
        """

        report_fields = report_data[0]["fields"]
        fields_to_subset = {
            "id":"id",
            "title":"title",
            "title_english":"title",
            "text": "body",
            "text_english": "body",
            "origin_url": "origin",
            "source_url": "url"
        }

        subset = {
            new_key: self.try_key(original_key, report_fields)
            for new_key, original_key in fields_to_subset.items()
            }

        subset["date"] = report_fields["date"]["original"]
        subset["country"] = report_fields["primary_country"]["name"]

        return subset
