import pytest
from unittest.mock import patch, MagicMock
from msftoolbox.dhis.module import DhisMetadata, DhisDataValues
import requests
import json

def test_dhismetadata_init():
    metadata = DhisMetadata(username='user', password='pass', server_url='http://example.com')
    assert metadata.dhis2_username == 'user'
    assert metadata.dhis2_password == 'pass'
    assert metadata.dhis2_server_url == 'http://example.com'

def test_dhismetadata_configure_dhis2_server():
    metadata = DhisMetadata(username='user', password='pass', server_url='http://example.com')
    metadata.configure_dhis2_server(username='newuser')
    assert metadata.dhis2_username == 'newuser'
    assert metadata.dhis2_password == 'pass'
    assert metadata.dhis2_server_url == 'http://example.com'

    metadata.configure_dhis2_server(password='newpass', server_url='http://newserver.com')
    assert metadata.dhis2_username == 'newuser'
    assert metadata.dhis2_password == 'newpass'
    assert metadata.dhis2_server_url == 'http://newserver.com'

    metadata.configure_dhis2_server(username=None, password=None, server_url=None)
    assert metadata.dhis2_username == 'newuser'
    assert metadata.dhis2_password == 'newpass'
    assert metadata.dhis2_server_url == 'http://newserver.com'

@patch('requests.get')
def test_get_response_success(mock_get):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {'key': 'value'}
    mock_get.return_value = mock_response

    metadata = DhisMetadata(username='user', password='pass', server_url='http://example.com')
    url = 'http://example.com/api/someendpoint'
    result = metadata.get_response(url)

    mock_get.assert_called_with(url, auth=('user', 'pass'), params=None)
    assert result == {'key': 'value'}

@patch('requests.get')
def test_get_response_auth_failure(mock_get):
    mock_response = MagicMock()
    mock_response.status_code = 401
    mock_response.raise_for_status.side_effect = requests.HTTPError('401 Client Error')
    mock_get.return_value = mock_response

    metadata = DhisMetadata(username='user', password='pass', server_url='http://example.com')
    url = 'http://example.com/api/someendpoint'

    with pytest.raises(ValueError, match='Authentication failed. Check your username and password.'):
        metadata.get_response(url)

    mock_get.assert_called_with(url, auth=('user', 'pass'), params=None)

@patch('requests.get')
def test_get_response_http_error(mock_get):
    mock_response = MagicMock()
    mock_response.status_code = 500
    mock_response.raise_for_status.side_effect = requests.HTTPError('500 Server Error')
    mock_get.return_value = mock_response

    metadata = DhisMetadata(username='user', password='pass', server_url='http://example.com')
    url = 'http://example.com/api/someendpoint'

    with pytest.raises(requests.HTTPError):
        metadata.get_response(url)

    mock_get.assert_called_with(url, auth=('user', 'pass'), params=None)

@patch('requests.get')
def test_get_response_invalid_json(mock_get):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.side_effect = json.JSONDecodeError('Expecting value', '', 0)
    mock_get.return_value = mock_response

    metadata = DhisMetadata(username='user', password='pass', server_url='http://example.com')
    url = 'http://example.com/api/someendpoint'

    with pytest.raises(json.JSONDecodeError):
        metadata.get_response(url)

    mock_get.assert_called_with(url, auth=('user', 'pass'), params=None)

def test_get_all_org_units():
    metadata = DhisMetadata(username='user', password='pass', server_url='http://example.com')
    metadata.get_response = MagicMock(return_value={'organisationUnits': [{'id': 'abc', 'name': 'Org Unit 1'}]})

    result = metadata.get_all_org_units(userOnly=True, paging=False)
    metadata.get_response.assert_called_with('http://example.com/api/organisationUnits', params={'userOnly': True, 'paging': False})
    assert result == [{'id': 'abc', 'name': 'Org Unit 1'}]

def test_get_org_unit_children():
    metadata = DhisMetadata(username='user', password='pass', server_url='http://example.com')
    metadata.get_response = MagicMock(return_value={'organisationUnits': [{'id': 'child1', 'name': 'Child Org Unit'}]})

    uid = 'parent1'
    result = metadata.get_org_unit_children(uid)
    expected_url = 'http://example.com/api/organisationUnits/parent1?includeChildren=true'
    metadata.get_response.assert_called_with(expected_url)
    assert result == [{'id': 'child1', 'name': 'Child Org Unit'}]

def test_get_data_sets_information():
    metadata = DhisMetadata(username='user', password='pass', server_url='http://example.com')

    def side_effect(url, params=None):
        if 'dataSets/uid1' in url:
            return {'id': 'uid1', 'name': 'DataSet 1'}
        elif 'dataSets/uid2' in url:
            return {'id': 'uid2', 'name': 'DataSet 2'}
        else:
            return {}

    metadata.get_response = MagicMock(side_effect=side_effect)
    data_sets_uids = ['uid1', 'uid2']
    result = metadata.get_data_sets_information(data_sets_uids)

    expected_calls = [
        ((f'http://example.com/api/dataSets/uid1',),),
        ((f'http://example.com/api/dataSets/uid2',),)
    ]
    assert metadata.get_response.call_args_list == expected_calls
    assert result == [{'id': 'uid1', 'name': 'DataSet 1'}, {'id': 'uid2', 'name': 'DataSet 2'}]

def test_get_data_sets_information_empty():
    metadata = DhisMetadata(username='user', password='pass', server_url='http://example.com')
    metadata.get_response = MagicMock()  # Mock the get_response method
    data_sets_uids = []
    result = metadata.get_data_sets_information(data_sets_uids)
    assert result == []
    metadata.get_response.assert_not_called()

def test_get_indicators():
    metadata = DhisMetadata(username='user', password='pass', server_url='http://example.com')
    metadata.get_response = MagicMock(return_value={'indicators': [{'id': 'ind1', 'name': 'Indicator 1'}]})

    result = metadata.get_indicators(paging=False)
    metadata.get_response.assert_called_with('http://example.com/api/indicators', params={'paging': False})
    assert result == [{'id': 'ind1', 'name': 'Indicator 1'}]

def test_get_data_elements():
    metadata = DhisMetadata(username='user', password='pass', server_url='http://example.com')
    metadata.get_response = MagicMock(return_value={'dataElements': [{'id': 'de1', 'name': 'Data Element 1'}]})

    result = metadata.get_data_elements(paging=False)
    metadata.get_response.assert_called_with('http://example.com/api/dataElements', params={'paging': False})
    assert result == [{'id': 'de1', 'name': 'Data Element 1'}]

def test_get_data_elements_for_org_unit():
    metadata = DhisMetadata(username='user', password='pass', server_url='http://example.com')

    def side_effect(url, params=None):
        if 'organisationUnits/orgUnit1?fields=dataSets' in url:
            return {
                'dataSets': [{'id': 'dataSet1'}, {'id': 'dataSet2'}]
            }
        elif 'dataSets/dataSet1?fields=dataSetElements[dataElement]' in url:
            return {
                'dataSetElements': [{'dataElement': {'id': 'de1', 'name': 'Data Element 1'}},
                                    {'dataElement': {'id': 'de2', 'name': 'Data Element 2'}}]
            }
        elif 'dataSets/dataSet2?fields=dataSetElements[dataElement]' in url:
            return {
                'dataSetElements': [{'dataElement': {'id': 'de3', 'name': 'Data Element 3'}}]
            }
        else:
            return {}

    metadata.get_response = MagicMock(side_effect=side_effect)
    org_unit_uid = 'orgUnit1'
    result = metadata.get_data_elements_for_org_unit(org_unit_uid)

    called_urls = [call_args[0][0] for call_args in metadata.get_response.call_args_list]
    expected_urls = [
        f'http://example.com/api/organisationUnits/{org_unit_uid}?fields=dataSets',
        f'http://example.com/api/dataSets/dataSet1?fields=dataSetElements[dataElement]',
        f'http://example.com/api/dataSets/dataSet2?fields=dataSetElements[dataElement]'
    ]
    assert called_urls == expected_urls

    expected_data_elements = [
        {'id': 'de1', 'name': 'Data Element 1'},
        {'id': 'de2', 'name': 'Data Element 2'},
        {'id': 'de3', 'name': 'Data Element 3'}
    ]
    assert result == expected_data_elements

def test_get_data_elements_for_org_unit_no_data_sets():
    metadata = DhisMetadata(username='user', password='pass', server_url='http://example.com')

    def side_effect(url, params=None):
        if 'organisationUnits/orgUnit1?fields=dataSets' in url:
            return {
                'dataSets': []
            }
        else:
            return {}

    metadata.get_response = MagicMock(side_effect=side_effect)
    org_unit_uid = 'orgUnit1'
    result = metadata.get_data_elements_for_org_unit(org_unit_uid)
    assert result == []
    assert len(metadata.get_response.call_args_list) == 1

def test_get_predictors():
    metadata = DhisMetadata(username='user', password='pass', server_url='http://example.com')
    metadata.get_response = MagicMock(return_value={'predictors': [{'id': 'pred1', 'name': 'Predictor 1'}]})

    result = metadata.get_predictors()
    metadata.get_response.assert_called_with('http://example.com/api/predictors')
    assert result == [{'id': 'pred1', 'name': 'Predictor 1'}]

@patch('requests.get')
def test_export_metadata(mock_get):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {'meta': 'data'}
    mock_get.return_value = mock_response

    metadata = DhisMetadata(username='user', password='pass', server_url='http://example.com')
    result = metadata.export_metadata(fields='id,name', indicators='true')

    expected_url = 'http://example.com/api/metadata'
    expected_params = {'fields': 'id,name', 'indicators': 'true'}
    mock_get.assert_called_with(expected_url, auth=('user', 'pass'), params=expected_params)
    assert result == {'meta': 'data'}

@patch('requests.get')
def test_export_metadata_http_error(mock_get):
    mock_response = MagicMock()
    mock_response.status_code = 500
    mock_response.raise_for_status.side_effect = requests.HTTPError('500 Server Error')
    mock_get.return_value = mock_response

    metadata = DhisMetadata(username='user', password='pass', server_url='http://example.com')
    with pytest.raises(requests.HTTPError):
        metadata.export_metadata(fields='id,name')

    expected_url = 'http://example.com/api/metadata'
    expected_params = {'fields': 'id,name'}
    mock_get.assert_called_with(expected_url, auth=('user', 'pass'), params=expected_params)

# Tests for DhisDataValues class

@patch('requests.post')
def test_send_data_values_json(mock_post):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {'status': 'SUCCESS'}
    mock_post.return_value = mock_response

    data_values = {'dataValues': [{'dataElement': 'de1', 'value': '10'}]}
    data_values_json = data_values

    datavalues = DhisDataValues(username='user', password='pass', server_url='http://example.com')
    result = datavalues.send_data_values(data_values_json, content_type='json', dryRun=True)

    expected_url = 'http://example.com/api/dataValueSets'
    expected_headers = {'Content-Type': 'application/json'}
    expected_params = {'dryRun': True}
    expected_data = json.dumps(data_values_json)
    mock_post.assert_called_with(expected_url, auth=('user', 'pass'), headers=expected_headers, params=expected_params, data=expected_data)
    assert result == {'status': 'SUCCESS'}

@patch('requests.post')
def test_send_data_values_xml(mock_post):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {'status': 'SUCCESS'}
    mock_post.return_value = mock_response

    data_values_xml = '<dataValueSet></dataValueSet>'
    datavalues = DhisDataValues(username='user', password='pass', server_url='http://example.com')
    result = datavalues.send_data_values(data_values_xml, content_type='xml', preheatCache=True)

    expected_url = 'http://example.com/api/dataValueSets'
    expected_headers = {'Content-Type': 'application/xml'}
    expected_params = {'preheatCache': True}
    expected_data = data_values_xml
    mock_post.assert_called_with(expected_url, auth=('user', 'pass'), headers=expected_headers, params=expected_params, data=expected_data)
    assert result == {'status': 'SUCCESS'}

@patch('requests.get')
def test_read_data_values(mock_get):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {'dataValues': [{'dataElement': 'de1', 'value': '10'}]}
    mock_get.return_value = mock_response

    datavalues = DhisDataValues(username='user', password='pass', server_url='http://example.com')
    result = datavalues.read_data_values(dataSet='ds1', period='202001', orgUnit='ou1')

    expected_url = 'http://example.com/api/dataValueSets'
    expected_params = {'dataSet': 'ds1', 'period': '202001', 'orgUnit': 'ou1'}
    mock_get.assert_called_with(expected_url, auth=('user', 'pass'), params=expected_params)
    assert result == {'dataValues': [{'dataElement': 'de1', 'value': '10'}]}

@patch('requests.delete')
def test_delete_data_value(mock_delete):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {'status': 'SUCCESS'}
    mock_delete.return_value = mock_response

    datavalues = DhisDataValues(username='user', password='pass', server_url='http://example.com')
    result = datavalues.delete_data_value(data_element='de1', period='202001', org_unit='ou1')

    expected_url = 'http://example.com/api/dataValues'
    expected_params = {'de': 'de1', 'pe': '202001', 'ou': 'ou1', 'co': None, 'cc': None}
    mock_delete.assert_called_with(expected_url, auth=('user', 'pass'), params=expected_params)
    assert result == {'status': 'SUCCESS'}

@patch('requests.post')
def test_send_individual_data_value(mock_post):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {'status': 'SUCCESS'}
    mock_post.return_value = mock_response

    data_value = {
        "dataElement": "fbfJHSPpUQD",
        "categoryOptionCombo": "PT59n8BQbqM",
        "period": "202201",
        "orgUnit": "DiszpKrYNg8",
        "value": "10",
        "comment": "OK"
    }

    datavalues = DhisDataValues(username='user', password='pass', server_url='http://example.com')
    result = datavalues.send_individual_data_value(data_value)

    expected_url = 'http://example.com/api/dataValues'
    expected_headers = {'Content-Type': 'application/json'}
    expected_data = json.dumps(data_value)
    mock_post.assert_called_with(expected_url, auth=('user', 'pass'), headers=expected_headers, data=expected_data)
    assert result == {'status': 'SUCCESS'}

@patch('requests.get')
def test_read_individual_data_value(mock_get):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {'dataValue': {'dataElement': 'de1', 'value': '10'}}
    mock_get.return_value = mock_response

    datavalues = DhisDataValues(username='user', password='pass', server_url='http://example.com')
    result = datavalues.read_individual_data_value(data_element='de1', period='202001', org_unit='ou1')

    expected_url = 'http://example.com/api/dataValues'
    expected_params = {'de': 'de1', 'pe': '202001', 'ou': 'ou1', 'co': None, 'cc': None}
    mock_get.assert_called_with(expected_url, auth=('user', 'pass'), params=expected_params)
    assert result == {'dataValue': {'dataElement': 'de1', 'value': '10'}}
