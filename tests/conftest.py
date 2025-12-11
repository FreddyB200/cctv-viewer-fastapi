"""Shared pytest fixtures for all tests."""
import pytest
from unittest.mock import MagicMock
from settings import Settings


@pytest.fixture
def mock_settings(monkeypatch):
    """Provide test Settings with fake camera configuration."""
    monkeypatch.setenv('CAM_USER', 'testuser')
    monkeypatch.setenv('CAM_PASS', 'testpass')
    monkeypatch.setenv('CAM_IP', '192.168.1.100')
    monkeypatch.setenv('CAM_PORT', '554')
    monkeypatch.setenv('TOTAL_CAMERAS', '4')
    return Settings()


@pytest.fixture
def mock_ffmpeg_process():
    """Mock FFmpeg process object."""
    process = MagicMock()
    process.poll.return_value = None  # Process is running
    process.stderr = MagicMock()
    process.stderr.read.return_value = b""
    return process


@pytest.fixture
def temp_index_html(tmp_path):
    """Create temporary index.html for testing."""
    html_content = '''<!DOCTYPE html>
<html><head><title>Test</title></head>
<body><div id="grid-container"></div></body></html>'''
    index_file = tmp_path / "index.html"
    index_file.write_text(html_content)
    return index_file
