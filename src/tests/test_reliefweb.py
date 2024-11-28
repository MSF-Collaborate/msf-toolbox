import pytest
import requests
from unittest.mock import patch, Mock
from msftoolbox.reliefweb.data import ReliefWebClient  # Replace with the actual module name

# Test ReliefWebClient initialization
def test_initialization():
    extractor = ReliefWebClient()
    assert extractor.app_name == "testing-rwapi"
    assert extractor.preset == "latest"
    assert extractor.limit == 50
    assert extractor.profile == "full"

# Test try_key method
def test_try_key():
    extractor = ReliefWebClient()
    data = {'title': 'Sample Report', 'key1': 'value1'}
    assert extractor.try_key('key1', data) == 'value1'
    assert extractor.try_key('key2', data) is None

# Test validate_date method
def test_validate_date():
    extractor = ReliefWebClient()
    assert extractor.validate_date("2023-10-01") is True
    assert extractor.validate_date("2023-02-30") is False
    assert extractor.validate_date("2023-13-01") is False
    assert extractor.validate_date("2023-10-32") is False

# Test list_reports with invalid date
def test_list_reports_invalid_date():
    extractor = ReliefWebClient()
    with pytest.raises(ValueError):
        extractor.list_reports("2023-10-01", "invalid-date", "query")

# Test list_reports with invalid query_operator
def test_list_reports_invalid_operator():
    extractor = ReliefWebClient()
    with pytest.raises(ValueError):
        extractor.list_reports("2023-10-01", "2023-10-02", "query", query_operator="INVALID")

# Mocking the requests.post for list_reports
@patch('requests.post')
def test_list_reports(mock_post):
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "data": [{
            "id": "1",
            "fields": {
                "title": "Sample Report",
                "source": [{"name": "Source1"}],
                "language": [{"name": "English"}],
                "date": {"original": "2023-10-01"},
            },
            "href": "https://example.com/report/1"
        }]
    }
    mock_post.return_value = mock_response

    extractor = ReliefWebClient()
    reports = extractor.list_reports("2023-10-01", "2023-10-02", "query")
    assert len(reports) == 1
    assert reports[0]["title"] == "Sample Report"

# Mocking the requests.get for get_report
@patch('requests.get')
def test_get_report(mock_get):
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "data": {
            "id": "1",
            "fields": {
                "title": "Sample Report",
                "body": "Report content"
            }
        }
    }
    mock_get.return_value = mock_response

    extractor = ReliefWebClient()
    report = extractor.get_report("https://example.com/report/1")
    assert report["fields"]["title"] == "Sample Report"

# Test HTTPError for list_reports
@patch('requests.post')
def test_list_reports_http_error(mock_post):
    mock_response = Mock()
    mock_response.status_code = 404
    mock_response.text = "Not Found"
    mock_post.return_value = mock_response

    extractor = ReliefWebClient()
    with pytest.raises(requests.HTTPError):
        extractor.list_reports("2023-10-01", "2023-10-02", "query")

# Test HTTPError for get_report
@patch('requests.get')
def test_get_report_http_error(mock_get):
    mock_response = Mock()
    mock_response.status_code = 404
    mock_response.text = "Not Found"
    mock_get.return_value = mock_response

    extractor = ReliefWebClient()
    with pytest.raises(requests.HTTPError):
        extractor.get_report("https://example.com/report/1")