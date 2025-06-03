import pytest
from unittest.mock import patch, MagicMock
from msftoolbox.dhis2.metadata import Dhis2MetadataClient
from msftoolbox.dhis2.data import Dhis2DataValuesClient
import requests
from requests.auth import HTTPBasicAuth
import json

def test_Dhis2MetadataClient_init():
    metadata = Dhis2MetadataClient(username='user', password='pass', server_url='http://example.com')
    assert metadata.dhis2_username == 'user'
    assert metadata.dhis2_password == 'pass'
    assert metadata.dhis2_server_url == 'http://example.com'

@patch('requests.get')
def test_get_response_success(mock_get):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {'key': 'value'}
    mock_get.return_value = mock_response

    metadata = Dhis2MetadataClient(username='user', password='pass', server_url='http://example.com')
    url = 'http://example.com/api/someendpoint'
    result = metadata.get_response(url)

    mock_get.assert_called_with(url, auth=HTTPBasicAuth('user', 'pass'), headers={}, params=None, timeout=10)
    assert result == {'key': 'value'}

@patch('requests.get')
def test_get_response_auth_failure(mock_get):
    mock_response = MagicMock()
    mock_response.status_code = 401
    mock_response.raise_for_status.side_effect = requests.HTTPError('401 Client Error')
    mock_get.return_value = mock_response

    metadata = Dhis2MetadataClient(username='user', password='pass', server_url='http://example.com')
    url = 'http://example.com/api/someendpoint'

    with pytest.raises(ValueError, match='Authentication failed. Check your username and password.'):
        metadata.get_response(url)

    mock_get.assert_called_with(url, auth=HTTPBasicAuth('user', 'pass'), headers={}, params=None, timeout=10)

@patch('requests.get')
def test_get_response_http_error(mock_get):
    mock_response = MagicMock()
    mock_response.status_code = 500
    mock_response.raise_for_status.side_effect = requests.HTTPError('500 Server Error')
    mock_get.return_value = mock_response

    metadata = Dhis2MetadataClient(username='user', password='pass', server_url='http://example.com')
    url = 'http://example.com/api/someendpoint'

    with pytest.raises(requests.HTTPError):
        metadata.get_response(url)

    mock_get.assert_called_with(url, auth=HTTPBasicAuth('user', 'pass'), headers={}, params=None, timeout=10)

@patch('requests.get')
def test_get_response_invalid_json(mock_get):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.side_effect = json.JSONDecodeError('Expecting value', '', 0)
    mock_get.return_value = mock_response

    metadata = Dhis2MetadataClient(username='user', password='pass', server_url='http://example.com')
    url = 'http://example.com/api/someendpoint'

    with pytest.raises(json.JSONDecodeError):
        metadata.get_response(url)

    mock_get.assert_called_with(url, auth=HTTPBasicAuth('user', 'pass'), headers={}, params=None, timeout=10)

def test_get_all_org_units():
    metadata = Dhis2MetadataClient(username='user', password='pass', server_url='http://example.com')
    metadata.get_response = MagicMock(return_value={'organisationUnits': [{'id': 'abc', 'name': 'Org Unit 1'}]})

    result = metadata.get_organisation_units(userOnly=True, paging=False)
    metadata.get_response.assert_called_with('http://example.com/api/organisationUnits', params={'userOnly': True, 'paging': False})
    assert result == [{'id': 'abc', 'name': 'Org Unit 1'}]

def test_get_org_unit_children():
    metadata = Dhis2MetadataClient(username='user', password='pass', server_url='http://example.com')
    metadata.get_response = MagicMock(return_value={'organisationUnits': [{'id': 'child1', 'name': 'Child Org Unit'}]})

    uid = 'parent1'
    result = metadata.get_org_unit_children(uid)
    expected_url = 'http://example.com/api/organisationUnits/parent1?includeChildren=true'
    metadata.get_response.assert_called_with(expected_url)
    assert result == [{'id': 'child1', 'name': 'Child Org Unit'}]

def test_get_indicators():
    metadata = Dhis2MetadataClient(username='user', password='pass', server_url='http://example.com')
    metadata.get_response = MagicMock(return_value={'indicators': [{'id': 'ind1', 'name': 'Indicator 1'}]})

    result = metadata.get_indicators(paging=False)
    metadata.get_response.assert_called_with('http://example.com/api/indicators', params={'paging': False})
    assert result == [{'id': 'ind1', 'name': 'Indicator 1'}]

def test_get_data_elements():
    metadata = Dhis2MetadataClient(username='user', password='pass', server_url='http://example.com')
    metadata.get_response = MagicMock(return_value={'dataElements': [{'id': 'de1', 'name': 'Data Element 1'}]})

    result = metadata.get_data_elements(paging=False)
    metadata.get_response.assert_called_with('http://example.com/api/dataElements', params={'paging': False})
    assert result == [{'id': 'de1', 'name': 'Data Element 1'}]

def test_get_datasets():
    metadata = Dhis2MetadataClient(username='user', password='pass', server_url='http://example.com')
    metadata.get_response = MagicMock(return_value={'dataSets': [{'id': 'ds1', 'name': 'DataSet 1'}]})

    result = metadata.get_datasets(paging=False)
    metadata.get_response.assert_called_with('http://example.com/api/dataSets', params={'paging': False})
    assert result == [{'id': 'ds1', 'name': 'DataSet 1'}]

def test_get_programs():
    metadata = Dhis2MetadataClient(username='user', password='pass', server_url='http://example.com')
    metadata.get_response = MagicMock(return_value={'programs': [{'id': 'pr1', 'name': 'Program 1'}]})

    result = metadata.get_programs(paging=False)
    metadata.get_response.assert_called_with('http://example.com/api/programs', params={'paging': False})
    assert result == [{'id': 'pr1', 'name': 'Program 1'}]

def test_get_program_stages():
    metadata = Dhis2MetadataClient(username='user', password='pass', server_url='http://example.com')
    metadata.get_response = MagicMock(return_value={'programStages': [{'id': 'ps1', 'name': 'Program Stage 1'}]})

    result = metadata.get_program_stages(paging=False)
    metadata.get_response.assert_called_with('http://example.com/api/programStages', params={'paging': False})
    assert result == [{'id': 'ps1', 'name': 'Program Stage 1'}]

def test_get_program_rules():
    metadata = Dhis2MetadataClient(username='user', password='pass', server_url='http://example.com')
    metadata.get_response = MagicMock(return_value={'programRules': [{'id': 'pr1', 'name': 'Program Rule 1'}]})

    result = metadata.get_program_rules(paging=False)
    metadata.get_response.assert_called_with('http://example.com/api/programRules', params={'paging': False})
    assert result == [{'id': 'pr1', 'name': 'Program Rule 1'}]

def test_get_indicator_groups():
    metadata = Dhis2MetadataClient(username='user', password='pass', server_url='http://example.com')
    metadata.get_response = MagicMock(return_value={'indicatorGroups': [{'id': 'ig1', 'name': 'Indicator Group 1'}]})

    result = metadata.get_indicator_groups(paging=False)
    metadata.get_response.assert_called_with('http://example.com/api/indicatorGroups', params={'paging': False})
    assert result == [{'id': 'ig1', 'name': 'Indicator Group 1'}]

def test_get_program_indicators():
    metadata = Dhis2MetadataClient(username='user', password='pass', server_url='http://example.com')
    metadata.get_response = MagicMock(return_value={'programIndicators': [{'id': 'pi1', 'name': 'Program Indicator 1'}]})

    result = metadata.get_program_indicators(paging=False)
    metadata.get_response.assert_called_with('http://example.com/api/programIndicators', params={'paging': False})
    assert result == [{'id': 'pi1', 'name': 'Program Indicator 1'}]

def test_get_program_indicator_groups():
    metadata = Dhis2MetadataClient(username='user', password='pass', server_url='http://example.com')
    metadata.get_response = MagicMock(return_value={'programIndicatorGroups': [{'id': 'pig1', 'name': 'Program Indicator Group 1'}]})

    result = metadata.get_program_indicator_groups(paging=False)
    metadata.get_response.assert_called_with('http://example.com/api/programIndicatorGroups', params={'paging': False})
    assert result == [{'id': 'pig1', 'name': 'Program Indicator Group 1'}]

def test_get_data_element_groups():
    metadata = Dhis2MetadataClient(username='user', password='pass', server_url='http://example.com')
    metadata.get_response = MagicMock(return_value={'dataElementGroups': [{'id': 'deg1', 'name': 'Data Element Group 1'}]})

    result = metadata.get_data_element_groups(paging=False)
    metadata.get_response.assert_called_with('http://example.com/api/dataElementGroups', params={'paging': False})
    assert result == [{'id': 'deg1', 'name': 'Data Element Group 1'}]

def test_get_option_sets():
    metadata = Dhis2MetadataClient(username='user', password='pass', server_url='http://example.com')
    metadata.get_response = MagicMock(return_value={'optionSets': [{'id': 'os1', 'name': 'Option Set 1'}]})

    result = metadata.get_option_sets(paging=False)
    metadata.get_response.assert_called_with('http://example.com/api/optionSets', params={'paging': False})
    assert result == [{'id': 'os1', 'name': 'Option Set 1'}]

def test_get_options():
    metadata = Dhis2MetadataClient(username='user', password='pass', server_url='http://example.com')
    metadata.get_response = MagicMock(return_value={'options': [{'id': 'o1', 'name': 'Option 1'}]})

    result = metadata.get_options(paging=False)
    metadata.get_response.assert_called_with('http://example.com/api/options', params={'paging': False})
    assert result == [{'id': 'o1', 'name': 'Option 1'}]

def test_get_data_elements_for_org_unit():
    metadata = Dhis2MetadataClient(username='user', password='pass', server_url='http://example.com')

    def side_effect(url):
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
        'http://example.com/api/dataSets/dataSet1?fields=dataSetElements[dataElement]',
        'http://example.com/api/dataSets/dataSet2?fields=dataSetElements[dataElement]'
    ]
    assert called_urls == expected_urls

    expected_data_elements = [
        {'id': 'de1', 'name': 'Data Element 1'},
        {'id': 'de2', 'name': 'Data Element 2'},
        {'id': 'de3', 'name': 'Data Element 3'}
    ]
    assert result == expected_data_elements

def test_get_data_elements_for_org_unit_no_data_sets():
    metadata = Dhis2MetadataClient(username='user', password='pass', server_url='http://example.com')

    def side_effect(url):
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
    metadata = Dhis2MetadataClient(username='user', password='pass', server_url='http://example.com')
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

    metadata = Dhis2MetadataClient(username='user', password='pass', server_url='http://example.com')
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

    metadata = Dhis2MetadataClient(username='user', password='pass', server_url='http://example.com')
    with pytest.raises(requests.HTTPError):
        metadata.export_metadata(fields='id,name')

    expected_url = 'http://example.com/api/metadata'
    expected_params = {'fields': 'id,name'}
    mock_get.assert_called_with(expected_url, auth=('user', 'pass'), params=expected_params)

# Tests for Dhis2DataValuesClient class

@patch('requests.post')
def test_send_data_values_json(mock_post):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {'status': 'SUCCESS'}
    mock_post.return_value = mock_response

    data_values = {'dataValues': [{'dataElement': 'de1', 'value': '10'}]}
    data_values_json = data_values

    datavalues = Dhis2DataValuesClient(username='user', password='pass', server_url='http://example.com')
    result = datavalues.send_data_values(data_values_json, content_type='json', dryRun=True)

    expected_url = 'http://example.com/api/dataValueSets'
    expected_headers = {'Content-Type': 'application/json'}
    expected_params = {'dryRun': True}
    expected_data = json.dumps(data_values_json)
    mock_post.assert_called_with(expected_url, auth=HTTPBasicAuth('user', 'pass'), headers=expected_headers, params=expected_params, data=expected_data, timeout=10)
    assert result == {'status': 'SUCCESS'}

@patch('requests.post')
def test_send_data_values_xml(mock_post):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {'status': 'SUCCESS'}
    mock_post.return_value = mock_response

    data_values_xml = '<dataValueSet></dataValueSet>'
    datavalues = Dhis2DataValuesClient(username='user', password='pass', server_url='http://example.com')
    result = datavalues.send_data_values(data_values_xml, content_type='xml', preheatCache=True)

    expected_url = 'http://example.com/api/dataValueSets'
    expected_headers = {'Content-Type': 'application/xml'}
    expected_params = {'preheatCache': True}
    expected_data = data_values_xml
    mock_post.assert_called_with(expected_url, auth=HTTPBasicAuth('user', 'pass'), headers=expected_headers, params=expected_params, data=expected_data, timeout=10)
    assert result == {'status': 'SUCCESS'}

@patch('requests.get')
def test_read_data_values(mock_get):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {'dataValues': [{'dataElement': 'de1', 'value': '10'}]}
    mock_get.return_value = mock_response

    datavalues = Dhis2DataValuesClient(username='user', password='pass', server_url='http://example.com')
    result = datavalues.read_data_values(dataSet='ds1', period='202001', orgUnit='ou1')

    expected_url = 'http://example.com/api/dataValueSets'
    expected_params = {'dataSet': 'ds1', 'period': '202001', 'orgUnit': 'ou1'}
    mock_get.assert_called_with(expected_url, auth=HTTPBasicAuth('user', 'pass'), params=expected_params, headers={}, timeout=10)
    assert result == {'dataValues': [{'dataElement': 'de1', 'value': '10'}]}

@patch('requests.delete')
def test_delete_data_value(mock_delete):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {'status': 'SUCCESS'}
    mock_delete.return_value = mock_response

    datavalues = Dhis2DataValuesClient(username='user', password='pass', server_url='http://example.com')
    result = datavalues.delete_data_value(data_element='de1', period='202001', org_unit='ou1')

    expected_url = 'http://example.com/api/dataValues'
    expected_params = {'de': 'de1', 'pe': '202001', 'ou': 'ou1', 'co': None, 'cc': None}
    mock_delete.assert_called_with(expected_url, auth=HTTPBasicAuth('user', 'pass'), params=expected_params, headers={}, timeout=10)
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

    datavalues = Dhis2DataValuesClient(username='user', password='pass', server_url='http://example.com')
    result = datavalues.send_individual_data_value(data_value)

    expected_url = 'http://example.com/api/dataValues'
    expected_headers = {'Content-Type': 'application/json'}
    expected_data = json.dumps(data_value)
    mock_post.assert_called_with(expected_url, auth=HTTPBasicAuth('user', 'pass'), headers=expected_headers, data=expected_data, timeout=10)
    assert result == {'status': 'SUCCESS'}

@patch('requests.get')
def test_read_individual_data_value(mock_get):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {'dataValue': {'dataElement': 'de1', 'value': '10'}}
    mock_get.return_value = mock_response

    datavalues = Dhis2DataValuesClient(username='user', password='pass', server_url='http://example.com')
    result = datavalues.read_individual_data_value(data_element='de1', period='202001', org_unit='ou1')

    expected_url = 'http://example.com/api/dataValues'
    expected_params = {'de': 'de1', 'pe': '202001', 'ou': 'ou1', 'co': None, 'cc': None}
    mock_get.assert_called_with(expected_url, auth=HTTPBasicAuth('user', 'pass'), params=expected_params, headers={}, timeout=10)
    assert result == {'dataValue': {'dataElement': 'de1', 'value': '10'}}
