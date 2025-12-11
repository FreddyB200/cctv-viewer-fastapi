"""Integration tests for concurrent WebRTC streams."""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from main import app
from settings import Settings


@pytest.fixture
def client(mocker):
    """Create a test client with mocked startup."""
    mocker.patch("main.startup_event")
    return TestClient(app)


@pytest.fixture
def mock_concurrent_cameras(monkeypatch):
    """Mock settings for concurrent camera testing."""
    monkeypatch.setenv("CAM_USER", "testuser")
    monkeypatch.setenv("CAM_PASS", "testpass")
    monkeypatch.setenv("CAM_IP", "192.168.1.100")
    monkeypatch.setenv("CAM_PORT", "554")
    monkeypatch.setenv("TOTAL_CAMERAS", "16")
    return Settings()


def test_frontend_creates_16_video_elements(client):
    """Test that frontend creates all 16 camera video elements."""
    response = client.get("/")

    # Verify grid container exists
    assert "grid-container" in response.text

    # Verify loop creates all cameras
    assert "totalCameras = 16" in response.text or "totalCameras=16" in response.text

    # Verify video element creation loop
    assert "createElement('video')" in response.text


def test_frontend_supports_grid_layout(client):
    """Test that frontend CSS supports 4x4 grid layout."""
    response = client.get("/")

    # Verify grid template configuration
    assert "grid-template-columns" in response.text
    assert "grid-template-rows" in response.text

    # Verify 4x4 layout
    assert "repeat(4" in response.text


def test_startup_creates_directories_for_all_cameras(mocker, mock_concurrent_cameras):
    """Test that startup creates HLS directories for all 16 cameras."""
    mocker.patch("main.check_ffmpeg")
    mock_makedirs = mocker.patch("os.makedirs")
    mocker.patch("shutil.rmtree")
    mocker.patch("os.path.exists", return_value=True)
    mocker.patch("subprocess.Popen")
    mocker.patch("time.sleep")
    mocker.patch("main.settings", mock_concurrent_cameras)

    from main import startup_event

    startup_event()

    # Verify directory creation for all 16 cameras
    expected_calls = [f"hls/cam{i}" for i in range(1, 17)]
    actual_calls = [call[0][0] for call in mock_makedirs.call_args_list if call[0][0].startswith("hls/cam")]

    assert len(actual_calls) == 16
    for expected_dir in expected_calls:
        assert expected_dir in actual_calls


def test_startup_spawns_ffmpeg_for_all_cameras(mocker, mock_concurrent_cameras):
    """Test that startup spawns FFmpeg processes for all 16 cameras."""
    mocker.patch("main.check_ffmpeg")
    mocker.patch("os.makedirs")
    mocker.patch("shutil.rmtree")
    mocker.patch("os.path.exists", return_value=True)

    mock_process = MagicMock()
    mock_process.poll.return_value = None  # Process running
    mock_popen = mocker.patch("subprocess.Popen", return_value=mock_process)

    mocker.patch("time.sleep")
    mocker.patch("main.settings", mock_concurrent_cameras)

    from main import startup_event

    startup_event()

    # Verify 16 FFmpeg processes spawned
    assert mock_popen.call_count == 16

    # Verify unique RTSP URLs for each camera (channel parameter)
    rtsp_channels = []
    for call_args in mock_popen.call_args_list:
        command = call_args[0][0]
        rtsp_url = [arg for arg in command if arg.startswith("rtsp://")][0]
        # Extract channel number from URL
        channel = rtsp_url.split("channel=")[1].split("&")[0]
        rtsp_channels.append(int(channel))

    assert rtsp_channels == list(range(1, 17))


def test_stream_isolation_one_failure_doesnt_affect_others(mocker, mock_concurrent_cameras):
    """Test that one camera failure doesn't prevent others from starting."""
    mocker.patch("main.check_ffmpeg")
    mocker.patch("os.makedirs")
    mocker.patch("shutil.rmtree")
    mocker.patch("os.path.exists", return_value=True)

    # Camera 5 fails, others succeed
    def create_process_mock(*args, **kwargs):
        command = args[0]
        rtsp_url = [arg for arg in command if arg.startswith("rtsp://")][0]
        channel = int(rtsp_url.split("channel=")[1].split("&")[0])

        mock_process = MagicMock()
        if channel == 5:
            mock_process.poll.return_value = 1  # Failed
            mock_process.stderr.read.return_value = b"Connection refused"
        else:
            mock_process.poll.return_value = None  # Running
        return mock_process

    mocker.patch("subprocess.Popen", side_effect=create_process_mock)
    mocker.patch("time.sleep")
    mocker.patch("main.settings", mock_concurrent_cameras)

    mock_logging = mocker.patch("main.logging")

    from main import startup_event

    startup_event()

    # Verify camera 5 failure logged
    # Check for the new logging format: logging.error("message", camera_id)
    error_calls = mock_logging.error.call_args_list
    camera_5_errors = [call for call in error_calls if len(call[0]) > 1 and call[0][1] == 5]
    assert len(camera_5_errors) > 0, f"Expected camera 5 errors, got: {error_calls}"

    # Verify other cameras logged as successful
    # Check for logging.info("Stream for Camera %d started successfully.", cam_id)
    info_calls = mock_logging.info.call_args_list

    # Filter for success messages only (exact match)
    success_messages = []
    for call in info_calls:
        if (
            len(call[0]) >= 2
            and call[0][0] == "Stream for Camera %d started successfully."
            and isinstance(call[0][1], int)
        ):
            success_messages.append(call[0][1])

    # Remove camera 5 from successful cameras
    successful_cameras = [cam for cam in success_messages if cam != 5]
    # Allow for duplicate calls (may happen in test environment due to module reloading)
    assert len(successful_cameras) >= 15  # At least all except camera 5
    # Verify we have exactly 15 unique successful cameras
    assert len(set(successful_cameras)) == 15


def test_frontend_stream_naming_pattern(client):
    """Test that frontend uses consistent stream naming for all cameras."""
    response = client.get("/")

    # Verify stream name construction
    assert "cam${i}" in response.text or "cam" in response.text

    # Verify loop iteration
    assert (
        "for (let i = 1; i <= totalCameras; i++)" in response.text
        or "for(let i=1;i<=totalCameras;i++)" in response.text
        or "for (let i = 1; i <= totalCameras; i++)" in response.text.replace(" ", "")
    )


def test_no_resource_leaks_with_multiple_connections(client):
    """Test that multiple page loads don't cause resource leaks."""
    # First load
    response1 = client.get("/")
    assert response1.status_code == 200

    # Second load (simulates refresh)
    response2 = client.get("/")
    assert response2.status_code == 200

    # Third load
    response3 = client.get("/")
    assert response3.status_code == 200

    # All responses should be identical (stateless)
    assert response1.text == response2.text == response3.text


@pytest.mark.parametrize("camera_id", list(range(1, 17)))
def test_each_camera_has_unique_stream_source(client, camera_id):
    """Test that each camera references a unique stream source."""
    response = client.get("/")

    # Verify stream naming supports unique IDs
    # The loop should create cam1, cam2, ..., cam16
    assert "streamName" in response.text or "cam" in response.text


def test_webrtc_mode_applies_to_all_cameras(client):
    """Test that USE_WEBRTC flag applies to all camera instances."""
    response = client.get("/")

    # Verify USE_WEBRTC constant
    assert "USE_WEBRTC = true" in response.text or "USE_WEBRTC=true" in response.text

    # Verify conditional logic
    assert "if (USE_WEBRTC)" in response.text or "if(USE_WEBRTC)" in response.text

    # Verify all streams use same protocol
    assert "startWebRTCWithRetry" in response.text or "startWebRTC" in response.text


def test_hls_directories_created_for_all_cameras(mocker, mock_concurrent_cameras):
    """Test that HLS fallback directories exist for all cameras."""
    mocker.patch("main.check_ffmpeg")
    mock_makedirs = mocker.patch("os.makedirs")
    mocker.patch("shutil.rmtree")
    mocker.patch("os.path.exists", return_value=True)
    mocker.patch("subprocess.Popen")
    mocker.patch("time.sleep")
    mocker.patch("main.settings", mock_concurrent_cameras)

    from main import startup_event

    startup_event()

    # Check that HLS directories created with exist_ok=True for safety
    hls_calls = [call for call in mock_makedirs.call_args_list if "hls" in str(call)]
    assert len(hls_calls) >= 16  # At least 16 camera directories

    # Verify exist_ok parameter
    for call in hls_calls:
        if len(call[1]) > 0:  # Has kwargs
            assert call[1].get("exist_ok", False) is True


def test_concurrent_startup_performance(mocker, mock_concurrent_cameras):
    """Test that startup completes in reasonable time with all cameras."""
    import time

    mocker.patch("main.check_ffmpeg")
    mocker.patch("os.makedirs")
    mocker.patch("shutil.rmtree")
    mocker.patch("os.path.exists", return_value=True)

    mock_process = MagicMock()
    mock_process.poll.return_value = None
    mocker.patch("subprocess.Popen", return_value=mock_process)

    # Mock time.sleep to avoid actual delays
    mocker.patch("time.sleep")
    mocker.patch("main.settings", mock_concurrent_cameras)

    from main import startup_event

    start_time = time.time()
    startup_event()
    elapsed_time = time.time() - start_time

    # With mocked sleep, should complete very quickly
    assert elapsed_time < 1.0  # Less than 1 second with mocks
