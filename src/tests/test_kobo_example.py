from unittest.mock import patch, Mock, MagicMock
import requests
from urllib.error import HTTPError
import pytest
from msftoolbox.kobo.kobo_mock import KoboClient

# define mocked values
api_token = "mock_api_token"
base_url = "https://kobo.example.com/"
client = KoboClient(base_url, api_token)
mock_results = {'results': [{'name': 'Asset1', 'uid': '123'}, {'name': 'Asset2', 'uid': '456'}]}
 
@patch('requests.get')
def test_list_assets(mock_get):
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = mock_results
    mock_get.return_value = mock_response

    assets = client.list_assets()
    mock_get.assert_called_with(f'{base_url}assets/', params=client.params, headers=client.headers)
    assert assets == [{'name': 'Asset1', 'uid': '123'}, {'name': 'Asset2', 'uid': '456'}], "Obtained asset list does not match expected mocked asset list"

@patch.object(KoboClient, 'list_assets', return_value=mock_results['results'])
def test_get_asset_uid(mock_list_assets):
    asset_uid = client.get_asset_uid('Asset2')
    assert asset_uid == '456', "Obtained UID does not match mocked UID"

@patch('requests.get')
def test_get_asset(mock_get):
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {'content': {'survey': []}}
    mock_get.return_value = mock_response

    asset = client.get_asset('123')
    mock_get.assert_called_with(f'{base_url}assets/123', params=client.params, headers=client.headers)
    assert asset == {'content': {'survey': []}}, "Content of specific asset does not match the mocked value"

@patch('requests.get')
def test_get_asset_data(mock_get):
    # Mock paginated response
    mock_response_page1 = Mock()
    mock_response_page1.status_code = 200
    mock_response_page1.json.return_value = {'results': [{'data': 'page1'}], 'next': f'{base_url}assets/123/data/page2'}

    mock_response_page2 = Mock()
    mock_response_page2.status_code = 200
    mock_response_page2.json.return_value = {'results': [{'data': 'page2'}], 'next': None}

    # Configure mock to return different responses based on URL
    # first call to mock_get() returns mock_response_page1, second call returns mock_response_page2
    mock_get.side_effect = [mock_response_page1, mock_response_page2]

    asset_data = client.get_asset_data('123')
    assert asset_data == [{'data': 'page1'}, {'data': 'page2'}], "Obtained asset data does not match expected data for two mocked pages"

@patch.object(KoboClient, 'get_asset', return_value={
    'content': {
        'survey': [
            {'type': 'text', 'name': 'question1','label': ['Question 1'], '$xpath': '/group/question1'},
            {'type': 'text', 'name': 'question1','label': ['Question 2']}
        ]
    }
})
def test_get_asset_metadata(mock_get_asset):
    metadata = client.get_asset_metadata('123')
    expected_metadata = [
        {'type': 'text', 'group': 'group', 'name': 'question1', 'label': ['Question 1'], 'hint': None, 'required': None, 'question_code': '/group/question1'},
        {'type': 'text', 'group': None, 'name': 'question2', 'label': ['Question 2'], 'hint': None, 'required': None, 'question_code': '/group/question2'}
    ]
    print(metadata)
    assert metadata == expected_metadata, "Expected metadata does not match mocked metadata"
