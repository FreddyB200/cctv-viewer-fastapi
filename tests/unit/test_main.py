"""Unit tests for main.py FastAPI application."""
import pytest
from unittest.mock import MagicMock, call, patch, mock_open
import main


def test_check_ffmpeg_success(mocker):
    """Test check_ffmpeg succeeds when FFmpeg is found."""
    mock_which = mocker.patch('shutil.which', return_value='/usr/bin/ffmpeg')
    mock_logging = mocker.patch('main.logging')

    main.check_ffmpeg()

    mock_which.assert_called_once_with('ffmpeg')
    mock_logging.info.assert_called_once_with('FFmpeg installation confirmed.')


def test_check_ffmpeg_not_found_raises_error(mocker):
    """Test check_ffmpeg raises RuntimeError when FFmpeg is not found."""
    mocker.patch('shutil.which', return_value=None)
    mock_logging = mocker.patch('main.logging')

    with pytest.raises(RuntimeError, match='FFmpeg not found'):
        main.check_ffmpeg()

    mock_logging.error.assert_called_once()


def test_startup_creates_hls_directories(mocker, mock_settings):
    """Test that startup_event creates HLS directories for all cameras."""
    mock_settings.TOTAL_CAMERAS = 4
    mocker.patch('main.settings', mock_settings)
    mocker.patch('main.check_ffmpeg')
    mock_makedirs = mocker.patch('os.makedirs')
    mocker.patch('shutil.rmtree')
    mocker.patch('os.path.exists', return_value=True)
    mocker.patch('subprocess.Popen')
    mocker.patch('time.sleep')

    main.startup_event()

    expected_calls = [
        call('hls/cam1', exist_ok=True),
        call('hls/cam2', exist_ok=True),
        call('hls/cam3', exist_ok=True),
        call('hls/cam4', exist_ok=True),
    ]
    mock_makedirs.assert_has_calls(expected_calls, any_order=True)


def test_startup_spawns_correct_ffmpeg_commands(mocker, mock_settings):
    """Test that startup_event spawns FFmpeg with correct RTSP URLs."""
    mock_settings.TOTAL_CAMERAS = 2
    mocker.patch('main.settings', mock_settings)
    mocker.patch('main.check_ffmpeg')
    mocker.patch('os.makedirs')
    mocker.patch('shutil.rmtree')
    mocker.patch('os.path.exists', return_value=True)
    mock_popen = mocker.patch('subprocess.Popen')
    mocker.patch('time.sleep')

    main.startup_event()

    assert mock_popen.call_count == 2

    # Verify RTSP URL construction
    first_call_args = mock_popen.call_args_list[0][0][0]
    expected_rtsp_url = (
        'rtsp://testuser:testpass@192.168.1.100:554'
        '/cam/realmonitor?channel=1&subtype=1'
    )
    assert expected_rtsp_url in first_call_args


def test_startup_validates_ffmpeg_processes(mocker, mock_settings):
    """Test that startup_event checks process health after 5s."""
    mock_settings.TOTAL_CAMERAS = 1
    mocker.patch('main.settings', mock_settings)
    mocker.patch('main.check_ffmpeg')
    mocker.patch('os.makedirs')
    mocker.patch('shutil.rmtree')
    mocker.patch('os.path.exists', return_value=True)

    mock_process = MagicMock()
    mock_process.poll.return_value = None  # Process still running
    mocker.patch('subprocess.Popen', return_value=mock_process)

    mock_sleep = mocker.patch('time.sleep')
    mock_logging = mocker.patch('main.logging')

    main.startup_event()

    mock_sleep.assert_called_once_with(5)
    mock_process.poll.assert_called_once()
    mock_logging.info.assert_any_call('Stream for Camera 1 started successfully.')


def test_startup_logs_failed_streams(mocker, mock_settings):
    """Test that startup_event logs errors for terminated processes."""
    mock_settings.TOTAL_CAMERAS = 1
    mocker.patch('main.settings', mock_settings)
    mocker.patch('main.check_ffmpeg')
    mocker.patch('os.makedirs')
    mocker.patch('shutil.rmtree')
    mocker.patch('os.path.exists', return_value=True)

    mock_process = MagicMock()
    mock_process.poll.return_value = 1  # Process terminated
    mock_process.stderr.read.return_value = b"Connection refused"
    mocker.patch('subprocess.Popen', return_value=mock_process)

    mocker.patch('time.sleep')
    mock_logging = mocker.patch('main.logging')

    main.startup_event()

    mock_logging.error.assert_any_call('FATAL: FFmpeg process for Camera 1 failed on startup.')
