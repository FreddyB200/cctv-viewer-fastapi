# file: settings.py
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional


class Settings(BaseSettings):
    # This tells Pydantic to read variables from a file named .env
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    # Camera Configuration (Required)
    CAM_USER: str
    CAM_PASS: str
    CAM_IP: str
    CAM_PORT: int
    TOTAL_CAMERAS: int

    # Security Configuration (Optional with defaults for development)
    # SECURITY WARNING: In production, always set ALLOWED_ORIGINS to your actual domain
    ALLOWED_ORIGINS: str = "*"  # Default allows all origins (development only)

    # TURN Server Configuration (Optional with public defaults)
    # SECURITY WARNING: In production, use private TURN infrastructure
    TURN_URL: Optional[str] = "turn:openrelay.metered.ca:80"
    TURN_USERNAME: Optional[str] = "openrelay"
    TURN_PASSWORD: Optional[str] = "openrelay"


# Create a single, reusable instance of the settings that we can import elsewhere
# Only instantiate if not in test environment (when .env is available)
try:
    settings = Settings()
except Exception:
    # During testing without .env, this is expected
    # Tests will mock settings as needed
    settings = None
