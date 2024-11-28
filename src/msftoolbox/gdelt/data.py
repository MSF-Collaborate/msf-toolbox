from datetime import datetime, timedelta
import requests
import newspaper

class GDELTClient:
    """
    A class to interact with the GDELT API.

    This class provides methods to list reports and download articles.
    """

    def __init__(
        self,
        sort="HybridRel",
        limit=50
        ):
        """
        Initialise the client and store configurations

        Args:
            sort (str, optional): The sorting mechanism for the API. Defaults to "HybridRel".
            limit (int, optional): The default value for the number of articles to list. Defaults to 50.
        """
        self.sort = sort
        self.limit = limit

    def list_reports(
        self,
        start_date: str,
        end_date: str,
        query_value: str,
        source_languages_filter: list = None,
        source_countries_filter: list = None,
        source_domains_filter: list = None
        ) -> list:
        """
        Retrieve a list of reports from the GDELT API based on specified criteria.

        Args:
            start_date (str): The start date for the reports in YYYY-MM-DD format.
            end_date (str): The end date for the reports in YYYY-MM-DD format.
            query_value (str): The search query value.
            source_countries_filter (list, optional): A list of source countries to filter the reports. This is different
                than filtering the content. To filter the content, use a keyword in query_value. Defaults to None.
            source_languages_filter (list, optional): A list of source languages to filter the reports. Defaults to ["english"].
            source_domains_filter (list, optional): A list of source domains to filter the reports. Defaults to None.

        Returns:
            list: A list of articles from the response data.

        Raises:
            HTTPError: If the HTTP request returns a status code other than 200.
            ValueError: If the request contains invalid arguments.
        """
        # Format dates and store url
        base_url = "https://api.gdeltproject.org/api/v2/doc/doc"
        dt_start_date = datetime.strptime(start_date, "%Y-%m-%d")
        dt_end_date = datetime.strptime(end_date, "%Y-%m-%d")
        api_formatted_start_date = datetime.strftime(dt_start_date, "%Y%m%d%H%M%S")
        api_formatted_end_date = datetime.strftime(dt_end_date, "%Y%m%d%H%M%S")

        # Apply default source language
        if source_languages_filter is None:
            source_languages_filter = ["english"]

        # Check validity of start and end date
        if dt_end_date - dt_start_date <= timedelta(0):
            raise ValueError("End date must be after start date")

        # Add the filters to the query value
        for gdelt_filter, optional_filter in [
            ("sourcecountry", source_countries_filter),
            ("sourcelang", source_languages_filter),
            ("domain", source_domains_filter)
            ]:
            if optional_filter is not None:
                temp_filter = " OR ".join(f"{gdelt_filter}:{value}" for value in optional_filter)
                temp_filter = f"({temp_filter})" if len(optional_filter) > 1 else temp_filter
                query_value = f"{query_value} AND {temp_filter}"

        # Create the payload
        params = {
            "query": query_value,
            "mode": "ArtList",
            "startdatetime": api_formatted_start_date,
            "enddatetime": api_formatted_end_date,
            "format": "JSON",
            "trans": "googtrans",
            "sort": self.sort,
            "maxrecords": self.limit
        }

        # Perform get request and process data. Assign message for failure.
        response = requests.get(base_url, params=params)
        response.raise_for_status()

        try:
            response_data = response.json()["articles"]
        except Exception:
            response_data = {"message": f"No articles returned. Response text: {response.text}"}

        return response_data

    def get_report(
        self,
        report_url: str
        ) -> dict:
        """Get a report based on the report url.

        Args:
            report_url (str): The url for the report. Typically the href from the list_reports response

        Returns:
            dict: Returns the article text containing the full report information or None if an error occurs.
        """
        try:
            page = newspaper.Article(report_url)
            page.download()
            page.parse()
            if page.text:
                return {"text": page.text}
            else:
                return {"text": None}
        except Exception as ex:
            print(f"Error downloading article from {report_url}: {str(ex)}")
            return {"text": None}
