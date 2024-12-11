import requests


class ModisClient:
    """
    A class to interact with the MODIS REST API for a specific product.
    A list of MODIS products can be found here: https://modis.ornl.gov/rst/api/v1/products
    """

    MODIS_API_URL = """https://modis.ornl.gov/rst/api/v1/"""

    def __init__(self, product, longitude, latitude):
        self.product = product
        self.longitude = longitude
        self.latitude = latitude

    def get_modis_product_dates(self):
        """
        MODIS releases data in 8-day cycles. This will return a list of valid dates in AYYYYDDD format.

        Returns:
            dict: A dictionary with a list of the valid MODIS and calendar dates.
        """
        date_url = f"{self.MODIS_API_URL}/{self.product}/dates?latitude={self.latitude}&longitude={self.longitude}"
        response = requests.get(date_url)

        response.raise_for_status()

        return response.json()

    def get_modis_product_bands(self):
        """
        List of bands available for the product.

        Returns:
            dict: A dictionary with a list of the available bands for the product.
        """
        date_url = f"{self.MODIS_API_URL}/{self.product}/bands"
        response = requests.get(date_url)

        response.raise_for_status()

        return response.json()

    def get_modis_product_data(
        self,
        band: str,
        start_date: str,
        end_date: str,
        km_above_below: int = 0,
        km_left_right: int = 0,
    ):
        """
        Get the MODIS data for a given date.

        Args:
            band (str): Data layer band.
            start_date (str): The start date in AYYYYDDD format.
            end_date (str): The end date in AYYYYDDD format.
            km_above_below (int): The number of km above and below the point.
            km_left_right (int): The number of km left and right of the point.

        Returns:
            dict: The data values from the MODIS REST API.
        """

        date_url = f"{self.MODIS_API_URL}/{self.product}/subset?latitude={self.latitude}&longitude={self.longitude}&band={band}&startDate={start_date}&endDate={end_date}&kmAboveBelow={km_above_below}&kmLeftRight={km_left_right}"
        response = requests.get(date_url)

        response.raise_for_status()

        return response.json()
