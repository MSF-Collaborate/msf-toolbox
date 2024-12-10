import pytest
from unittest.mock import patch, Mock
import requests
from msftoolbox.gdelt.data import GDELTClient  # Replace with the actual module name

# Test GDELTClient initialization
def test_initialization():
    extractor = GDELTClient()
    assert extractor.sort == "HybridRel"
    assert extractor.limit == 50

# Test list_reports with invalid date range
def test_list_reports_invalid_date():
    extractor = GDELTClient()
    with pytest.raises(ValueError):
        extractor.list_reports("2023-10-02", "2023-10-01", "query")

# Mocking the requests.get for list_reports
@patch('requests.get')
def test_list_reports(mock_get):
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "articles": [
            {"title": "Sample Article", "url": "https://example.com/article/1"}
        ]
    }
    mock_get.return_value = mock_response

    extractor = GDELTClient()
    articles = extractor.list_reports("2023-10-01", "2023-10-02", "query")
    assert len(articles) == 1
    assert articles[0]["title"] == "Sample Article"

# Test HTTPError for list_reports
@patch('requests.get')
def test_list_reports_http_error(mock_get):
    mock_response = Mock()
    mock_response.status_code = 404
    mock_response.text = "Not Found"
    mock_response.raise_for_status.side_effect = requests.HTTPError("Not Found")
    mock_get.return_value = mock_response

    extractor = GDELTClient()
    with pytest.raises(requests.HTTPError):
        extractor.list_reports("2023-10-01", "2023-10-02", "query")

# Mocking the newspaper.Article for get_report
@patch('newspaper.Article')
def test_get_report(mock_article):
    mock_article_instance = mock_article.return_value
    mock_article_instance.download = Mock()
    mock_article_instance.parse = Mock()
    mock_article_instance.text = "Full article text"

    extractor = GDELTClient()
    report = extractor.get_report("https://example.com/article/1")
    assert report["text"] == "Full article text"

# Test error handling in get_report
@patch('newspaper.Article')
def test_get_report_error(mock_article):
    mock_article_instance = mock_article.return_value
    mock_article_instance.download.side_effect = Exception("Download error")

    extractor = GDELTClient()
    report = extractor.get_report("https://example.com/article/1")
    assert report["text"] is None