import asyncio
import logging

from aiogram import Bot, Dispatcher

from app.config import settings
from app.handlers.common import router as common_router
from app.handlers.media import router as media_router
from app.services.audio_processor import AudioProcessor
from app.services.channel_assets import ChannelAssetsService
from app.services.media_publisher import MediaPublisherService
from app.utils.logging_setup import setup_logging

logger = logging.getLogger(__name__)


async def main() -> None:
    setup_logging()

    if settings.BOT_TOKEN == "PASTE_YOUR_BOT_TOKEN_HERE":
        raise ValueError("BOT_TOKEN ni app/config.py ichida kiriting.")

    bot = Bot(token=settings.BOT_TOKEN)
    dp = Dispatcher()

    channel_assets = ChannelAssetsService(
        bot=bot,
        channel_id=settings.CHANNEL_ID,
        default_thumbnail_path=settings.DEFAULT_THUMBNAIL_PATH,
    )
    audio_processor = AudioProcessor()
    media_service = MediaPublisherService(
        bot=bot,
        channel_id=settings.CHANNEL_ID,
        channel_assets=channel_assets,
        audio_processor=audio_processor,
        unknown_artist=settings.DEFAULT_UNKNOWN_ARTIST,
    )

    dp.include_router(common_router)
    dp.include_router(media_router)

    logger.info("Bot is starting...")
    try:
        await dp.start_polling(bot, media_service=media_service)
    finally:
        await bot.session.close()
        logger.info("Bot stopped")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("Bot interrupted by user")
