"""Integration tests for FastAPI endpoints."""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, mock_open
from main import app


@pytest.fixture
def client(mocker):
    """Create a test client with mocked startup."""
    mocker.patch("main.startup_event")
    return TestClient(app)


def test_health_check_returns_ok(client):
    """Test /health endpoint returns correct JSON."""
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_get_frontend_returns_html(client, mocker):
    """Test / endpoint returns index.html content."""
    html_content = '<html><body><div id="grid-container"></div></body></html>'
    mocker.patch("builtins.open", mock_open(read_data=html_content))

    response = client.get("/")

    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
    assert "grid-container" in response.text


def test_get_frontend_contains_webrtc_code(client, mocker):
    """Test that frontend contains WebRTC functionality."""
    with open("/workspace/index.html", "r") as f:
        html_content = f.read()

    mocker.patch("builtins.open", mock_open(read_data=html_content))

    response = client.get("/")

    assert "RTCPeerConnection" in response.text
    assert "startWebRTC" in response.text
    assert "grid-container" in response.text


def test_ice_servers_endpoint_returns_config(client, mocker):
    """Test /api/ice-servers endpoint returns ICE configuration."""
    mock_settings = mocker.MagicMock()
    mock_settings.TURN_URL = "turn:turn.example.com:3478"
    mock_settings.TURN_USERNAME = "testuser"
    mock_settings.TURN_PASSWORD = "testpass"

    with mocker.patch("main.settings", mock_settings):
        response = client.get("/api/ice-servers")

    assert response.status_code == 200
    data = response.json()
    assert "iceServers" in data
    assert len(data["iceServers"]) == 2  # STUN + TURN

    # Check STUN server
    stun_server = data["iceServers"][0]
    assert "stun:stun.l.google.com:19302" in stun_server["urls"]

    # Check TURN server
    turn_server = data["iceServers"][1]
    assert "turn:turn.example.com:3478" in turn_server["urls"]
    assert turn_server["username"] == "testuser"
    assert turn_server["credential"] == "testpass"


def test_ice_servers_endpoint_without_turn_credentials(client, mocker):
    """Test /api/ice-servers endpoint when TURN credentials are not set."""
    mock_settings = mocker.MagicMock()
    mock_settings.TURN_URL = None
    mock_settings.TURN_USERNAME = None
    mock_settings.TURN_PASSWORD = None

    with mocker.patch("main.settings", mock_settings):
        response = client.get("/api/ice-servers")

    assert response.status_code == 200
    data = response.json()
    assert "iceServers" in data
    # Should only have STUN server when TURN is not configured
    assert len(data["iceServers"]) == 1
    assert "stun:stun.l.google.com:19302" in data["iceServers"][0]["urls"]


def test_ice_servers_endpoint_with_default_turn(client, mocker):
    """Test /api/ice-servers endpoint with default public TURN server."""
    mock_settings = mocker.MagicMock()
    mock_settings.TURN_URL = "turn:openrelay.metered.ca:80"
    mock_settings.TURN_USERNAME = "openrelay"
    mock_settings.TURN_PASSWORD = "openrelay"

    with mocker.patch("main.settings", mock_settings):
        response = client.get("/api/ice-servers")

    assert response.status_code == 200
    data = response.json()
    assert len(data["iceServers"]) == 2
    turn_server = data["iceServers"][1]
    assert "turn:openrelay.metered.ca:80" in turn_server["urls"]
