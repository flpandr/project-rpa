import pytest
from unittest.mock import Mock, patch
from src.api.client import APIClient
from src.utils.exceptions import APIError
import requests

@pytest.fixture
def api_client():
    return APIClient("https://api.test.com")

@pytest.fixture
def mock_response():
    mock = Mock()
    mock.json.return_value = {"data": "test"}
    mock.raise_for_status.return_value = None
    return mock

def test_api_client_initialization():
    client = APIClient("https://test.com")
    assert client.base_url == "https://test.com"
    assert client.timeout > 0
    assert client.max_retries > 0

@patch('requests.Session.get')
def test_get_success(mock_get, api_client, mock_response):
    mock_get.return_value = mock_response
    result = api_client.get("test-endpoint")
    assert result == {"data": "test"}
    mock_get.assert_called_once()

@patch('requests.Session.get')
def test_get_retry_on_failure(mock_get, api_client, mock_response):
    mock_get.side_effect = [
        requests.exceptions.RequestException(),
        requests.exceptions.RequestException(),
        requests.exceptions.RequestException()
    ]
    
    with pytest.raises(APIError):
        api_client.get("test-endpoint")
    assert mock_get.call_count == api_client.max_retries

def test_send_report_email(api_client):
    result = api_client.send_report_email(
        "test@example.com",
        "report.pdf",
        "Test Report",
        10,
        150.5
    )
    assert result is True

@patch('requests.Session.get')
def test_get_paginated(mock_get, api_client, mock_response):
    mock_response.json.return_value = [{"id": 1}, {"id": 2}]
    mock_get.return_value = mock_response
    
    results = api_client.get_paginated("test-endpoint")
    assert len(results) > 0
    assert isinstance(results, list)
