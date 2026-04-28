from __future__ import annotations

import io
import logging
from pathlib import Path

from aiogram import Bot
from aiogram.types import BufferedInputFile, Message

from app.services.audio_processor import AudioProcessor
from app.services.channel_assets import ChannelAssetsService

logger = logging.getLogger(__name__)


class MediaPublisherService:
    """Accepts media from users and republishes it to the configured channel."""

    def __init__(
        self,
        bot: Bot,
        channel_id: int,
        channel_assets: ChannelAssetsService,
        audio_processor: AudioProcessor,
        unknown_artist: str,
    ) -> None:
        self.bot = bot
        self.channel_id = channel_id
        self.channel_assets = channel_assets
        self.audio_processor = audio_processor
        self.unknown_artist = unknown_artist

    async def publish_audio(self, message: Message) -> None:
        audio_source = message.audio or message.document
        if audio_source is None:
            raise ValueError("Audio source not found")

        channel_context = await self.channel_assets.get_context()
        source_bytes = await self._download_telegram_file(audio_source.file_id)

        original_artist = getattr(audio_source, "performer", None) or getattr(audio_source, "title", None) or self.unknown_artist
        generated_title = f"{channel_context.title} - {original_artist}"
        performer = channel_context.title
        source_name = getattr(audio_source, "file_name", None) or "track.mp3"

        try:
            file_name, processed_bytes = await self.audio_processor.process(
                source_bytes=source_bytes,
                source_name=source_name,
                new_title=generated_title,
                performer=performer,
                cover_bytes=channel_context.thumbnail_bytes,
            )
        except Exception:
            logger.exception("Audio retagging failed. Falling back to original bytes.")
            file_name = Path(source_name).name
            processed_bytes = source_bytes

        await self.bot.send_audio(
            chat_id=self.channel_id,
            audio=BufferedInputFile(processed_bytes, filename=file_name),
            title=generated_title,
            performer=performer,
            thumbnail=BufferedInputFile(channel_context.thumbnail_bytes, filename="thumb.jpg"),
        )

    async def publish_image(self, message: Message) -> None:
        channel_context = await self.channel_assets.get_context()

        if message.photo:
            photo = message.photo[-1]
            image_bytes = await self._download_telegram_file(photo.file_id)
            await self.bot.send_photo(
                chat_id=self.channel_id,
                photo=BufferedInputFile(image_bytes, filename="photo.jpg"),
                caption=channel_context.title,
            )
            return

        if message.document and self._is_image_document(message.document.mime_type, message.document.file_name):
            image_bytes = await self._download_telegram_file(message.document.file_id)
            image_name = message.document.file_name or "image.jpg"
            await self.bot.send_photo(
                chat_id=self.channel_id,
                photo=BufferedInputFile(image_bytes, filename=image_name),
                caption=channel_context.title,
            )
            return

        raise ValueError("Image source not found")

    async def _download_telegram_file(self, file_id: str) -> bytes:
        telegram_file = await self.bot.get_file(file_id)
        buffer = io.BytesIO()
        await self.bot.download_file(telegram_file.file_path, destination=buffer)
        return buffer.getvalue()

    @staticmethod
    def _is_image_document(mime_type: str | None, file_name: str | None) -> bool:
        if mime_type and mime_type.startswith("image/"):
            return True
        if file_name and Path(file_name).suffix.lower() in {".jpg", ".jpeg", ".png", ".webp"}:
            return True
        return False

    @staticmethod
    def is_audio_message(message: Message) -> bool:
        if message.audio:
            return True
        if not message.document:
            return False
        if message.document.mime_type and message.document.mime_type.startswith("audio/"):
            return True
        if message.document.file_name and Path(message.document.file_name).suffix.lower() in {".mp3", ".m4a", ".mp4"}:
            return True
        return False

    @staticmethod
    def is_image_message(message: Message) -> bool:
        if message.photo:
            return True
        if not message.document:
            return False
        return MediaPublisherService._is_image_document(message.document.mime_type, message.document.file_name)
