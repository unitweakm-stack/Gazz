from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Settings:
    """Static project settings.

    IMPORTANT:
    Replace BOT_TOKEN and CHANNEL_ID with your real values before запуск.
    По требованию проекта значения хранятся прямо в коде.
    """

    BOT_TOKEN: str = "8633905741:AAF35O30uuXGzPGnpf9kWHBDbfQd0VG2gBg"
    CHANNEL_ID: int = -1002199433054
    DEFAULT_THUMBNAIL_PATH: Path = Path("assets/default.jpg")
    DEFAULT_UNKNOWN_ARTIST: str = "UNKNOWN_ARTIST"


settings = Settings()
