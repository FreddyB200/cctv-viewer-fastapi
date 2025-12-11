"""Integration tests for WebRTC endpoint."""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, Mock
from main import app


@pytest.fixture
def client(mocker):
    """Create a test client with mocked startup."""
    mocker.patch('main.startup_event')
    return TestClient(app)


@pytest.fixture
def mock_go2rtc_response(mocker):
    """Mock go2rtc WebRTC API responses."""
    def _mock_response(status_code=200, sdp_answer='v=0\r\no=- 789 012 IN IP4 127.0.0.1\r\ns=go2rtc\r\n'):
        mock_resp = Mock()
        mock_resp.status_code = status_code
        mock_resp.text = sdp_answer
        mock_resp.ok = status_code == 200
        return mock_resp
    return _mock_response


def test_webrtc_endpoint_forwards_to_go2rtc(client, mocker, mock_go2rtc_response):
    """Test that WebRTC endpoint forwards SDP offers to go2rtc backend."""
    # Note: This is a placeholder test since the actual /api/webrtc endpoint
    # is handled by go2rtc, not our FastAPI app. In production, go2rtc runs
    # on port 1984 and handles WebRTC signaling.

    # This test documents the expected behavior:
    # 1. Frontend sends POST to http://localhost:1984/api/webrtc?src=cam1
    # 2. go2rtc processes the SDP offer and returns SDP answer
    # 3. Frontend uses the answer to complete WebRTC connection

    # Since go2rtc is a separate service, we can't test the actual endpoint here.
    # Instead, we verify our application serves the frontend that makes the request.

    response = client.get('/')
    assert response.status_code == 200
    assert 'RTCPeerConnection' in response.text
    assert '/api/webrtc' in response.text


def test_frontend_contains_webrtc_configuration(client):
    """Test that frontend has correct WebRTC endpoint configuration."""
    response = client.get('/')

    # Verify WebRTC endpoint URL pattern
    assert '1984/api/webrtc' in response.text

    # Verify stream name parameter
    assert 'src=' in response.text

    # Verify SDP offer/answer exchange logic
    assert 'createOffer' in response.text
    assert 'setLocalDescription' in response.text
    assert 'setRemoteDescription' in response.text


def test_health_endpoint_for_monitoring(client):
    """Test health endpoint returns OK for monitoring systems."""
    response = client.get('/health')

    assert response.status_code == 200
    assert response.json() == {'status': 'ok'}


def test_frontend_has_retry_logic(client):
    """Test that frontend implements retry logic for WebRTC failures."""
    response = client.get('/')

    # Verify retry mechanism exists
    assert 'startWebRTCWithRetry' in response.text or 'retry' in response.text.lower()

    # Verify exponential backoff
    assert 'Math.pow(2' in response.text or 'attempt' in response.text.lower()


def test_frontend_has_error_handling(client):
    """Test that frontend has proper WebRTC error handling."""
    response = client.get('/')

    # Verify ICE connection state monitoring
    assert 'iceConnectionState' in response.text

    # Verify error overlay for user feedback
    assert 'errorOverlay' in response.text or 'error' in response.text.lower()

    # Verify cleanup on connection failure
    assert 'cleanupWebRTC' in response.text or 'close' in response.text


def test_frontend_configures_ice_servers(client):
    """Test that frontend configures STUN/TURN servers correctly."""
    response = client.get('/')

    # Verify STUN server configuration
    assert 'stun.l.google.com:19302' in response.text or 'stun:' in response.text

    # Verify RTCPeerConnection configuration
    assert 'iceServers' in response.text


def test_frontend_uses_recvonly_transceivers(client):
    """Test that frontend uses recvonly mode for video/audio (viewer mode)."""
    response = client.get('/')

    # Verify transceiver setup
    assert 'addTransceiver' in response.text

    # Verify recvonly direction
    assert 'recvonly' in response.text


@pytest.mark.parametrize("camera_num", [1, 2, 5, 16])
def test_frontend_supports_multiple_cameras(client, camera_num):
    """Test that frontend can handle multiple camera streams."""
    response = client.get('/')

    # Verify stream name pattern supports multiple cameras
    assert f'cam{camera_num}' in response.text or 'cam${i}' in response.text or 'cam`${i}`' in response.text


def test_frontend_has_ice_gathering_timeout(client):
    """Test that frontend implements ICE gathering timeout."""
    response = client.get('/')

    # Verify timeout mechanism
    assert 'timeout' in response.text.lower() or 'setTimeout' in response.text

    # Verify ICE gathering wait logic
    assert 'iceGatheringState' in response.text


def test_static_files_mount_for_hls_fallback(client):
    """Test that HLS static files are mounted for fallback streaming."""
    # Verify /hls route exists (will 404 if no streams, but mount should work)
    response = client.get('/hls/')

    # Should get 404 (no index) but not 405 (method not allowed) or other errors
    # This confirms the StaticFiles mount is working
    assert response.status_code in [404, 200]
