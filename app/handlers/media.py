import logging

from aiogram import Router
from aiogram.types import Message

from app.services.media_publisher import MediaPublisherService

router = Router(name=__name__)
logger = logging.getLogger(__name__)


@router.message()
async def media_entrypoint(message: Message, media_service: MediaPublisherService) -> None:
    try:
        if media_service.is_audio_message(message):
            await media_service.publish_audio(message)
            await message.answer("✅ Audio kanalga yuborildi.")
            return

        if media_service.is_image_message(message):
            await media_service.publish_image(message)
            await message.answer("✅ Rasm kanalga yuborildi.")
            return

        await message.answer("❌ Faqat audio yoki rasm yuboring.")
    except Exception:
        logger.exception("Failed to process incoming message")
        await message.answer("❌ Xatolik yuz berdi. Qaytadan urinib ko‘ring.")
