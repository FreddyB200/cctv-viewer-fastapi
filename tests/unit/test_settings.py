"""Unit tests for settings.py configuration loading."""
import pytest
from pydantic import ValidationError
from settings import Settings


def test_settings_loads_from_env(monkeypatch):
    """Test that Settings correctly loads from environment variables."""
    monkeypatch.setenv('CAM_USER', 'testuser')
    monkeypatch.setenv('CAM_PASS', 'testpass')
    monkeypatch.setenv('CAM_IP', '192.168.1.100')
    monkeypatch.setenv('CAM_PORT', '554')
    monkeypatch.setenv('TOTAL_CAMERAS', '16')

    settings = Settings()

    assert settings.CAM_USER == 'testuser'
    assert settings.CAM_PASS == 'testpass'
    assert settings.CAM_IP == '192.168.1.100'
    assert settings.CAM_PORT == 554
    assert settings.TOTAL_CAMERAS == 16


def test_settings_validates_port_type(monkeypatch):
    """Test that CAM_PORT must be a valid integer."""
    monkeypatch.setenv('CAM_USER', 'testuser')
    monkeypatch.setenv('CAM_PASS', 'testpass')
    monkeypatch.setenv('CAM_IP', '192.168.1.100')
    monkeypatch.setenv('CAM_PORT', 'not_a_number')
    monkeypatch.setenv('TOTAL_CAMERAS', '16')

    with pytest.raises(ValidationError):
        Settings()


def test_settings_raises_on_missing_variable(monkeypatch):
    """Test that Settings raises ValidationError when required variable is missing."""
    monkeypatch.setenv('CAM_USER', 'testuser')
    monkeypatch.delenv('CAM_PASS', raising=False)

    with pytest.raises(ValidationError) as exc_info:
        Settings()

    assert 'CAM_PASS' in str(exc_info.value)


def test_settings_validates_total_cameras_type(monkeypatch):
    """Test that TOTAL_CAMERAS must be a valid integer."""
    monkeypatch.setenv('CAM_USER', 'testuser')
    monkeypatch.setenv('CAM_PASS', 'testpass')
    monkeypatch.setenv('CAM_IP', '192.168.1.100')
    monkeypatch.setenv('CAM_PORT', '554')
    monkeypatch.setenv('TOTAL_CAMERAS', 'sixteen')

    with pytest.raises(ValidationError):
        Settings()
