import pytest
import requests
from unittest.mock import patch, Mock

from msftoolbox.modis.data import ModisClient


@pytest.fixture
def mock_valid_modis_dates_return_value():
    dates = {
        "dates": [
            {"modis_date": "A2024273", "calendar_date": "2024-09-29"},
            {"modis_date": "A2024281", "calendar_date": "2024-10-07"},
            {"modis_date": "A2024289", "calendar_date": "2024-10-15"},
        ]
    }
    return dates


@pytest.fixture
def mock_valid_modis_bands_return_value():
    bands = {
        "bands": [
            {
                "band": "sur_refl_b01",
                "description": "Surface_reflectance_for_band_1",
                "units": "reflectance",
                "valid_range": "-100 to 16000",
                "fill_value": "-28672",
                "scale_factor": "0.0001",
                "add_offset": "0",
            },
            {
                "band": "sur_refl_b02",
                "description": "Surface_reflectance_for_band_2",
                "units": "reflectance",
                "valid_range": "-100 to 16000",
                "fill_value": "-28672",
                "scale_factor": "0.0001",
                "add_offset": "0",
            },
        ]
    }
    return bands


@pytest.fixture
def mock_modis_data_return_value():
    data = {
        "xllcorner": "803384.27",
        "yllcorner": "3564728.00",
        "cellsize": 463.312716528,
        "nrows": 1,
        "ncols": 1,
        "band": "sur_refl_b01",
        "units": "reflectance",
        "scale": "0.0001",
        "latitude": 32.061,
        "longitude": 8.527,
        "header": "https://modisrest.ornl.gov/rst/api/v1/MOD09A1/subset?latitude=32.061&longitude=8.527&band=sur_refl_b01&startDate=A2024281&endDate=A2024289&kmAboveBelow=0&kmLeftRight=0",
        "subset": [
            {
                "modis_date": "A2024281",
                "calendar_date": "2024-10-07",
                "band": "sur_refl_b01",
                "tile": "h18v05",
                "proc_date": "2024290063229",
                "data": [4307],
            },
            {
                "modis_date": "A2024289",
                "calendar_date": "2024-10-15",
                "band": "sur_refl_b01",
                "tile": "h18v05",
                "proc_date": "2024298145543",
                "data": [4534],
            },
        ],
    }
    return data


@patch("msftoolbox.modis.data.requests.get")
def test_get_modis_product_dates_success(mock_get, mock_valid_modis_dates_return_value):
    test_client = ModisClient("MOD09A1", 32.061, 8.527)

    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = mock_valid_modis_dates_return_value
    mock_get.return_value = mock_response

    result = test_client.get_modis_product_dates()
    assert result == {
        "dates": [
            {"modis_date": "A2024273", "calendar_date": "2024-09-29"},
            {"modis_date": "A2024281", "calendar_date": "2024-10-07"},
            {"modis_date": "A2024289", "calendar_date": "2024-10-15"},
        ]
    }


@patch("msftoolbox.modis.data.requests.get")
def test_get_modis_product_dates_product_not_found(mock_get):
    modis_client = ModisClient("MOD09AB", 32.061, 8.527)
    mock_response = Mock()
    mock_response.status_code = 404
    mock_response.text = "Product MOD09AB not found."
    mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError(
        f"404 Client Error: Not Found for url: {mock_response.text}"
    )
    mock_get.return_value = mock_response

    with pytest.raises(requests.exceptions.HTTPError) as exc_info:
        modis_client.get_modis_product_dates()

    assert "404 Client Error" in str(exc_info.value)
    assert "Product MOD09AB not found." in str(exc_info.value)


@patch("msftoolbox.modis.data.requests.get")
def test_get_modis_product_bands_success(mock_get, mock_valid_modis_bands_return_value):
    test_client = ModisClient("MOD09A1", 32.061, 8.527)

    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = mock_valid_modis_bands_return_value
    mock_get.return_value = mock_response

    result = test_client.get_modis_product_bands()
    assert result == mock_valid_modis_bands_return_value


@patch("msftoolbox.modis.data.requests.get")
def test_get_modis_product_data_success(mock_get, mock_modis_data_return_value):
    modis_client = ModisClient("MOD09A1", 32.061, 8.527)
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = mock_modis_data_return_value
    mock_get.return_value = mock_response

    result = modis_client.get_modis_product_data("sur_refl_b01", "A2024281", "A2024289")

    assert result == mock_modis_data_return_value


@patch("msftoolbox.modis.data.requests.get")
def test_get_modis_product_data_invalid_band(mock_get):
    modis_client = ModisClient("MOD09AB", 32.061, 8.527)
    mock_response = Mock()
    mock_response.status_code = 404
    mock_response.text = "Invalid band test_band for product MOD09A1."
    mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError(
        f"404 Client Error: Not Found for url: {mock_response.text}"
    )
    mock_get.return_value = mock_response

    with pytest.raises(requests.exceptions.HTTPError) as exc_info:
        modis_client.get_modis_product_data("sur_refl_b01", "A2024281", "A2024289")

    assert "404 Client Error" in str(exc_info.value)
    assert "Invalid band test_band for product MOD09A1." in str(exc_info.value)
