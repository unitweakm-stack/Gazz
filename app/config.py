from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Settings:
    """Static project settings.

    IMPORTANT:
    Replace BOT_TOKEN and CHANNEL_ID with your real values before запуск.
    По требованию проекта значения хранятся прямо в коде.
    """

    BOT_TOKEN: str = "PASTE_YOUR_BOT_TOKEN_HERE"
    CHANNEL_ID: int = -1001234567890
    DEFAULT_THUMBNAIL_PATH: Path = Path("assets/default.jpg")
    DEFAULT_UNKNOWN_ARTIST: str = "UNKNOWN_ARTIST"


settings = Settings()
