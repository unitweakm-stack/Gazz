from __future__ import annotations

import io
import logging
from dataclasses import dataclass
from pathlib import Path

from aiogram import Bot
from PIL import Image

logger = logging.getLogger(__name__)


@dataclass(slots=True)
class ChannelContext:
    title: str
    thumbnail_bytes: bytes


class ChannelAssetsService:
    """Loads channel title and thumbnail with fallback to local asset."""

    def __init__(self, bot: Bot, channel_id: int, default_thumbnail_path: Path) -> None:
        self.bot = bot
        self.channel_id = channel_id
        self.default_thumbnail_path = default_thumbnail_path

    async def get_context(self) -> ChannelContext:
        chat = await self.bot.get_chat(self.channel_id)
        channel_title = chat.title or "MY_CHANNEL"
        thumbnail_bytes = await self._load_channel_thumbnail(chat.photo.big_file_id if chat.photo else None)
        return ChannelContext(title=channel_title, thumbnail_bytes=thumbnail_bytes)

    async def _load_channel_thumbnail(self, file_id: str | None) -> bytes:
        if not file_id:
            logger.info("Channel photo not found. Using default thumbnail.")
            return self._load_default_thumbnail()

        try:
            telegram_file = await self.bot.get_file(file_id)
            buffer = io.BytesIO()
            await self.bot.download_file(telegram_file.file_path, destination=buffer)
            return self._normalize_thumbnail(buffer.getvalue())
        except Exception:
            logger.exception("Failed to download channel photo. Using default thumbnail.")
            return self._load_default_thumbnail()

    def _load_default_thumbnail(self) -> bytes:
        return self._normalize_thumbnail(self.default_thumbnail_path.read_bytes())

    @staticmethod
    def _normalize_thumbnail(image_bytes: bytes) -> bytes:
        with Image.open(io.BytesIO(image_bytes)) as image:
            image = image.convert("RGB")
            image.thumbnail((320, 320))

            output = io.BytesIO()
            quality = 92
            image.save(output, format="JPEG", quality=quality, optimize=True)

            while output.tell() > 190 * 1024 and quality > 55:
                output = io.BytesIO()
                quality -= 5
                image.save(output, format="JPEG", quality=quality, optimize=True)

            return output.getvalue()
