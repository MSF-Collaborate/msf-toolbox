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

#done; harcode the url/token? or use above params?

def test_KoboClient_init():
    kobo = KoboClient(base_url = base_url, api_token =api_token )
    assert kobo.base_url == "https://kobo.example.com/"
    assert kobo.headers == {'Authorization': f'Token ''mock_api_token'}

# :TODO # add auth_test in class
# add auth test; mock 401
# @patch('requests.get')
# def test_KoboClient_auth():
#     mock_response = Mock()
#     mock_response.msg = 401
#     mock_response.text = {"detail":"Invalid token."}
#     mock_response.text = {"detail":"Invalid token."}
#     {
#                     "Authenticated": False,
#                     "Status_code": response.status_code,
#                     "Error": response.text
#                 }
#     assert kobo.headers == 'Authentication failed. Status: 401, Error: {"detail":"Invalid token."}' 


@patch('requests.get')
def test_authentication_failure(mock_get):
    # Mock failed authentication response
    mock_response = Mock()
    mock_response.status_code = 401
    mock_response.json.return_value = {'Authenticated': False, 'Error': 'Unauthorized'}
    mock_get.return_value = mock_response

    with mock_get.assertRaises(RuntimeError) as context:
        KoboClient(base_url="https://kobo.example.com/", api_token='invalid_token')
    
    mock_get.assertIn("Authentication failed", str(context.exception))
    print("Test passed: Authentication failed with invalid token.")


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
    #TODO: adjust pagination example url
    mock_response_page1.json.return_value = {'results': [{'data': 'page1'}], 'next': f'{base_url}assets/123/data/page2'}

    mock_response_page2 = Mock()
    mock_response_page2.status_code = 200
    mock_response_page2.json.return_value = {'results': [{'data': 'page2'}], 'next': None}

    # Configure mock to return different responses based on URL
    # first call to mock_get() returns mock_response_page1, second call returns mock_response_page2
    mock_get.side_effect = [mock_response_page1, mock_response_page2]

    asset_data = client.get_asset_data('123')
    assert asset_data == [{'data': 'page1'}, {'data': 'page2'}], "Obtained asset data does not match expected data for two mocked pages"


#Done
@patch.object(KoboClient, 'get_asset', return_value={
    'content': {
        'survey': [
              {'name': 'ASSESSMENT_DATE',   'type': 'date',   'label': ['Date of assessment', 'Date de l’évaluation'],   '$xpath': 'ASSESSMENT_DATE',  'required': True},
              {'name': 'Question_1',  'type': 'select_one',  'label': ['1. Full question written in English', '1. Full question written in another language'],   '$xpath': 'RPT1/GRP1/Question_1',   'required': None  },
        ]
    }
})
def test_get_asset_metadata(mock_get_asset):
    metadata = client.get_asset_metadata('123')
    expected_metadata = [
        {'type': 'date', 'group': None, 'name': 'ASSESSMENT_DATE', 'label': ['Date of assessment', 'Date de l’évaluation'], 'hint': None, 'required': True, 'question_code': 'ASSESSMENT_DATE'},
        {'type': 'select_one', 'group': 'GRP1', 'name': 'Question_1', 'label': ['1. Full question written in English', '1. Full question written in another language'], 'hint': None, 'required': None, 'question_code': 'RPT1/GRP1/Question_1'}
        
    ]

    assert metadata == expected_metadata, "Expected metadata does not match mocked metadata"
