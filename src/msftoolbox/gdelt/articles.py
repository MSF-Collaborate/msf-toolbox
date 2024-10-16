from datetime import datetime
import requests
from urllib.error import HTTPError
import newspaper

class GDELTExtractor:
    def __init__(
        self,
        sort="HybridRel",
        limit=50,
        mode="ArtList"
    ):
        self.sort = sort
        self.mode = mode
        self.limit = limit

    def format_date(self, date) -> str:
        date = datetime.strptime(date, "%Y-%m-%d")
        return datetime.strftime(date, "%Y%m%d%H%M%S")

    def list_reports(
        self,
        start_date: str,
        end_date: str,
        query_value: str,
        country_filter: list = None,
        response_format: str = "JSON"
    ) -> list:
        base_url = "https://api.gdeltproject.org/api/v2/doc/doc"
        start_date = self.format_date(start_date)
        end_date = self.format_date(end_date)

        params = {
            "query": f"{query_value} AND {country_filter}",
            "mode": self.mode,
            "startdatetime": start_date,
            "enddatetime": end_date,
            "format": response_format,
            "trans": "googtrans"
        }

        response = requests.get(base_url, params=params)
        if response.status_code != 200:
            raise HTTPError(f"HTTP error: {response.status_code}")

        response_data = response.json()["articles"]
        return response_data

    def get_report(self, report_url: str) -> dict:
        """Get a report based on the report url.

        Args:
            report_url (str): The url for the report. Typically the href from the list_reports response

        Returns:
            dict: A dictionary containing the full report information or None if an error occurs.
        """
        try:
            page = newspaper.Article(report_url)
            page.download()
            page.parse()
            if page.text:
                return {"text": page.text}
            else:
                return {"text": None}
        except Exception as e:
            print(f"Error downloading article from {report_url}: {str(e)}")
            return {"text": None}
