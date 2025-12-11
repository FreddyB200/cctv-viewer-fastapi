"""Integration tests for FastAPI endpoints."""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, mock_open
from main import app


@pytest.fixture
def client(mocker):
    """Create a test client with mocked startup."""
    mocker.patch('main.startup_event')
    return TestClient(app)


def test_health_check_returns_ok(client):
    """Test /health endpoint returns correct JSON."""
    response = client.get('/health')

    assert response.status_code == 200
    assert response.json() == {'status': 'ok'}


def test_get_frontend_returns_html(client, mocker):
    """Test / endpoint returns index.html content."""
    html_content = '<html><body><div id="grid-container"></div></body></html>'
    mocker.patch('builtins.open', mock_open(read_data=html_content))

    response = client.get('/')

    assert response.status_code == 200
    assert 'text/html' in response.headers['content-type']
    assert 'grid-container' in response.text


def test_get_frontend_contains_webrtc_code(client, mocker):
    """Test that frontend contains WebRTC functionality."""
    with open('/workspace/index.html', 'r') as f:
        html_content = f.read()

    mocker.patch('builtins.open', mock_open(read_data=html_content))

    response = client.get('/')

    assert 'RTCPeerConnection' in response.text
    assert 'startWebRTC' in response.text
    assert 'grid-container' in response.text
