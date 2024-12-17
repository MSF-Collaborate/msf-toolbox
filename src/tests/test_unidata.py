from urllib.error import HTTPError
import pytest
from unittest.mock import patch, MagicMock
import requests
from msftoolbox.unidata.data import UniDataAPIClient  # Replace 'your_module' with the actual module name

def test_UniDataAPIClient_init():
    client = UniDataAPIClient(username='user', password='pass', server_url='https://example.com')
    assert client.username == 'user'
    assert client.password == 'pass'
    assert client.server_url == 'https://example.com'

def test_UniDataAPIClient_configure_unidata_server():
    client = UniDataAPIClient(username='user', password='pass', server_url='https://example.com')
    assert client.username == 'user'
    assert client.password == 'pass'
    assert client.server_url == 'https://example.com'

    client.configure_unidata_server(username='newuser', password='newpass', server_url='https://newserver.com')
    assert client.username == 'newuser'
    assert client.password == 'newpass'
    assert client.server_url == 'https://newserver.com'

@patch('requests.get')
def test_get_response_success(mock_get):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {'key': 'value'}
    mock_get.return_value = mock_response

    client = UniDataAPIClient(username='user', password='pass', server_url='https://example.com')
    endpoint = '/api/someendpoint'
    result = client.get_response(endpoint)

    expected_url = 'https://example.com/api/someendpoint'
    expected_params = {'login': 'user', 'password': 'pass'}
    mock_get.assert_called_with(expected_url, params=expected_params, timeout=client.timeout)
    assert result == {'key': 'value'}

@patch('requests.get')
def test_get_response_auth_failure(mock_get):
    mock_response = MagicMock()
    mock_response.status_code = 401
    mock_response.raise_for_status.side_effect = requests.HTTPError('401 Client Error')
    mock_get.return_value = mock_response

    client = UniDataAPIClient(username='user', password='pass', server_url='https://example.com')
    endpoint = '/api/someendpoint'

    with pytest.raises(HTTPError, match='Authentication failed. Check your username and password.'):
        client.get_response(endpoint)

    expected_url = 'https://example.com/api/someendpoint'
    expected_params = {'login': 'user', 'password': 'pass'}
    mock_get.assert_called_with(expected_url, params=expected_params, timeout=client.timeout)

@patch('requests.get')
def test_get_response_http_error(mock_get):
    mock_response = MagicMock()
    mock_response.status_code = 500
    mock_response.raise_for_status.side_effect = requests.HTTPError('500 Server Error')
    mock_get.return_value = mock_response

    client = UniDataAPIClient(username='user', password='pass', server_url='https://example.com')
    endpoint = '/api/someendpoint'

    with pytest.raises(requests.HTTPError):
        client.get_response(endpoint)

    expected_url = 'https://example.com/api/someendpoint'
    expected_params = {'login': 'user', 'password': 'pass'}
    mock_get.assert_called_with(expected_url, params=expected_params, timeout=client.timeout)

@patch('requests.get')
def test_get_articles(mock_get):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {'articles': [{'id': 'art1', 'title': 'Article 1'}]}
    mock_get.return_value = mock_response

    client = UniDataAPIClient(username='user', password='pass', server_url='https://example.com')
    result = client.get_articles(mode=1)

    expected_url = 'https://example.com/articles'
    expected_params = {'login': 'user', 'password': 'pass', 'mode': 1}
    mock_get.assert_called_with(expected_url, params=expected_params, timeout=client.timeout)
    assert result == {'articles': [{'id': 'art1', 'title': 'Article 1'}]}

@patch('requests.get')
def test_get_subcatalogues(mock_get):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {'subcatalogues': [{'id': 'sc1', 'name': 'Subcatalogue 1'}]}
    mock_get.return_value = mock_response

    client = UniDataAPIClient(username='user', password='pass', server_url='https://example.com')
    result = client.get_subcatalogues()

    expected_url = 'https://example.com/lists'
    expected_params = {'login': 'user', 'password': 'pass'}
    mock_get.assert_called_with(expected_url, params=expected_params, timeout=client.timeout)
    assert result == {'subcatalogues': [{'id': 'sc1', 'name': 'Subcatalogue 1'}]}

@patch('requests.get')
def test_get_intros(mock_get):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {'intros': [{'id': 'intro1', 'content': 'Intro Content'}]}
    mock_get.return_value = mock_response

    client = UniDataAPIClient(username='user', password='pass', server_url='https://example.com')
    result = client.get_intros()

    expected_url = 'https://example.com/intros'
    expected_params = {'login': 'user', 'password': 'pass'}
    mock_get.assert_called_with(expected_url, params=expected_params, timeout=client.timeout)
    assert result == {'intros': [{'id': 'intro1', 'content': 'Intro Content'}]}

@patch('requests.get')
def test_get_checklists(mock_get):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {'checklists': [{'id': 'cl1', 'name': 'Checklist 1'}]}
    mock_get.return_value = mock_response

    client = UniDataAPIClient(username='user', password='pass', server_url='https://example.com')
    result = client.get_checklists()

    expected_url = 'https://example.com/checklists'
    expected_params = {'login': 'user', 'password': 'pass'}
    mock_get.assert_called_with(expected_url, params=expected_params, timeout=client.timeout)
    assert result == {'checklists': [{'id': 'cl1', 'name': 'Checklist 1'}]}