from datetime import datetime, timedelta
import requests
import newspaper

class GDELTExtractor:
    def __init__(
        self,
        sort="HybridRel",
        limit=50
        ):
        self.sort = sort
        self.limit = limit

    def list_reports(
        self,
        start_date: str,
        end_date: str,
        query_value: str,
        country_filter: list = None,
        mode: str = "ArtList"
    ) -> list:
        """
        Retrieve a list of reports from the GDELT API based on specified criteria.

        Args:
            start_date (str): The start date for the reports in YYYY-MM-DD format.
            end_date (str): The end date for the reports in YYYY-MM-DD format.
            query_value (str): The search query value.
            country_filter (list, optional): A list of countries to filter the reports. Defaults to None.
            response_format (str, optional): The format of the response, default is "JSON".
            mode (str, optional): The mode for the API request, default is "ArtList".

        Returns:
            list: A list of articles from the response data.

        Raises:
            HTTPError: If the HTTP request returns a status code other than 200.
        """
        base_url = "https://api.gdeltproject.org/api/v2/doc/doc"
        dt_start_date = datetime.strptime(start_date, "%Y-%m-%d")
        dt_end_date = datetime.strptime(end_date, "%Y-%m-%d")
        api_formatted_start_date = datetime.strftime(dt_start_date, "%Y%m%d%H%M%S")
        api_formatted_end_date = datetime.strftime(dt_end_date, "%Y%m%d%H%M%S")

        if dt_end_date - dt_start_date <= timedelta(0):
            raise ValueError("End date must be after start date")

        params = {
            "query": f"{query_value} AND {country_filter}",
            "mode": mode,
            "startdatetime": api_formatted_start_date,
            "enddatetime": api_formatted_end_date,
            "format": "JSON",
            "trans": "googtrans"
        }

        response = requests.get(base_url, params=params)
        response.raise_for_status()

        response_data = response.json()["articles"]
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
