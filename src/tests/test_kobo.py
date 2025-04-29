from unittest.mock import patch, Mock
from msftoolbox.kobo.data import KoboClient

# Mocked API token and base URL
API_TOKEN = "mock_api_token"
BASE_URL = "https://kobo.example.com/"
MOCK_ASSET_ID_01 = "gh3NsxvpoBmltERFuKcVnD"
MOCK_ASSET_ID_02 = "tk7QwzjbiGvypNXUfLsCmH"

# Mocked assets
mock_results = {
    'results': [
        {'name': 'Asset1', 'uid': f'{MOCK_ASSET_ID_01}'},
        {'name': 'Asset2', 'uid': f'{MOCK_ASSET_ID_02}'}
    ]
}

# Mocked asset content
mock_asset_content = {
    'content': {
        'survey': [
            {'name': 'SURVEY_START_TIME', 'type': 'start'}
        ]
    }
}

# Mocked paginated asset data
mock_asset_data_page1 = {'results': [{'data': 'page1'}], 'next': f'{BASE_URL}assets/{MOCK_ASSET_ID_01}/data?format=json&limit=30000&start=30000'}
mock_asset_data_page2 = {'results': [{'data': 'page2'}], 'next': None}

# Mocked asset metadata
mock_asset_metadata = {
    'content': {
        'survey': [
            {'name': 'ASSESSMENT_DATE', 'type': 'date', 'label': ['Date of assessment', 'Date de l’évaluation'], '$xpath': 'ASSESSMENT_DATE', 'required': True},
            {'name': 'Question_1', 'type': 'select_one', 'label': ['1. Full question written in English', '1. Full question written in another language'], '$xpath': 'RPT1/GRP1/Question_1', 'required': None}
        ]
    }
}

# Mocked asset dictionary with choice items
mock_asset_with_choices = {
    'content': {
        'choices': [
            {'list_name': 'yes_no', 'name': 'YES', 'label': ['Yes']},
            {'list_name': 'yes_no', 'name': 'NO', 'label': ['No']}
        ]
    }
}

# Test for listing assets
@patch.object(KoboClient, '_check_auth', return_value={"Authenticated": True, "Status_code": 200})
def test_list_assets(mock_check_auth):
    client = KoboClient(base_url=BASE_URL, api_token=API_TOKEN)
    with patch('requests.get') as mock_get:
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = mock_results
        mock_get.return_value = mock_response

        assets = client.list_assets()
        mock_get.assert_called_with(f'{BASE_URL}assets/', params=client.params, headers=client.headers)
        assert assets == mock_results['results'], "Asset list does not match expected results"


# Test for getting asset UID
@patch.object(KoboClient, '_check_auth', return_value={"Authenticated": True, "Status_code": 200})
@patch.object(KoboClient, 'list_assets', return_value=mock_results['results'])
def test_get_asset_uid(mock_list_assets, mock_check_auth):
    client = KoboClient(base_url=BASE_URL, api_token=API_TOKEN)
    asset_uid = client.get_asset_uid('Asset2')
    assert asset_uid == f'{MOCK_ASSET_ID_02}', "UID does not match expected value"
    mock_list_assets.assert_called_once()


# Test for getting specific asset details
@patch.object(KoboClient, '_check_auth', return_value={"Authenticated": True, "Status_code": 200})
def test_get_asset(mock_check_auth):
    client = KoboClient(base_url=BASE_URL, api_token=API_TOKEN)
    with patch('requests.get') as mock_get:
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = mock_asset_content
        mock_get.return_value = mock_response

        asset = client.get_asset(MOCK_ASSET_ID_01)
        mock_get.assert_called_with(f'{BASE_URL}assets/{MOCK_ASSET_ID_01}', params=client.params, headers=client.headers)
        assert asset == mock_asset_content, "Asset content does not match expected value"


# Test for getting paginated asset data
@patch.object(KoboClient, '_check_auth', return_value={"Authenticated": True, "Status_code": 200})
def test_get_asset_data(mock_check_auth):
    client = KoboClient(base_url=BASE_URL, api_token=API_TOKEN)
    with patch('requests.get') as mock_get:
        mock_response_page1 = Mock()
        mock_response_page1.status_code = 200
        mock_response_page1.json.return_value = mock_asset_data_page1

        mock_response_page2 = Mock()
        mock_response_page2.status_code = 200
        mock_response_page2.json.return_value = mock_asset_data_page2

        mock_get.side_effect = [mock_response_page1, mock_response_page2]

        asset_data = client.get_asset_data(MOCK_ASSET_ID_01)
        assert asset_data == [{'data': 'page1'}, {'data': 'page2'}], "Paginated asset data does not match expected results"


# Test for getting asset metadata
@patch.object(KoboClient, '_check_auth', return_value={"Authenticated": True, "Status_code": 200})
@patch.object(KoboClient, 'get_asset', return_value=mock_asset_metadata)
def test_get_asset_metadata(mock_get_asset, mock_check_auth):
    client = KoboClient(base_url=BASE_URL, api_token=API_TOKEN)
    metadata = client.get_asset_metadata(MOCK_ASSET_ID_01)
    expected_metadata = [
        {'type': 'date', 'group': None, 'name': 'ASSESSMENT_DATE', 'label': ['Date of assessment', 'Date de l’évaluation'], 'hint': None, 'required': True, 'question_code': 'ASSESSMENT_DATE'},
        {'type': 'select_one', 'group': 'GRP1', 'name': 'Question_1', 'label': ['1. Full question written in English', '1. Full question written in another language'], 'hint': None, 'required': None, 'question_code': 'RPT1/GRP1/Question_1'}
    ]
    assert metadata == expected_metadata, "Metadata does not match expected results"


# Test for the get_asset_choice_items method
@patch.object(KoboClient, '_check_auth', return_value={"Authenticated": True, "Status_code": 200})
@patch.object(KoboClient, 'get_asset', return_value=mock_asset_with_choices)
def test_get_asset_choice_items(mock_get_asset, mock_check_auth):
    client = KoboClient(base_url=BASE_URL, api_token=API_TOKEN)

    # Call the get_asset_choice_items method
    choice_items = client.get_asset_choice_items(MOCK_ASSET_ID_01)

    # Expected output
    expected_choice_items = [
        {'list_name': 'yes_no', 'name': 'YES', 'label': ['Yes']},
        {'list_name': 'yes_no', 'name': 'NO', 'label': ['No']}
    ]

    # Assert that the extracted choice items match the expected results
    assert choice_items == expected_choice_items, "Extracted choice items do not match expected results"
