import logging
import os
import asyncio
from aiohttp import web
from mutagen.id3 import ID3, APIC
from mutagen.flac import FLAC
from mutagen.mp4 import MP4
from PIL import Image
import io

from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
)

from config import BOT_TOKEN, CHANNEL_ID, ADMIN_ID

# To'g'ri qo'shtirnoqlar bilan logging sozlamalari
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

# =============================================
# UPTIME ROBOT UCHUN WEB SERVER
# =============================================

async def health_check(request):
    return web.Response(text="OK - Bot ishlayapti!", status=200)

async def start_web_server():
    app_web = web.Application()
    app_web.router.add_get("/", health_check)
    app_web.router.add_get("/health", health_check)

    runner = web.AppRunner(app_web)
    await runner.setup()

    # Railway PORT env o'zgaruvchisini avtomatik beradi
    port = int(os.environ.get("PORT", 8080))
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()
    logger.info(f"Web server port {port} da ishga tushdi")

# =============================================
# YORDAMCHI FUNKSIYALAR
# =============================================

def extract_metadata(file_path: str) -> dict:
    metadata = {"title": None, "artist": None, "cover": None}
    try:
        ext = os.path.splitext(file_path)[1].lower()
        if ext == ".mp3":
            audio = ID3(file_path)
            if "TIT2" in audio:
                metadata["title"] = str(audio["TIT2"])
            if "TPE1" in audio:
                metadata["artist"] = str(audio["TPE1"])
            for tag in audio.values():
                if isinstance(tag, APIC):
                    metadata["cover"] = tag.data
                    break
        elif ext == ".flac":
            audio = FLAC(file_path)
            metadata["title"] = audio.get("title", [None])[0]
            metadata["artist"] = audio.get("artist", [None])[0]
            pics = audio.pictures
            if pics:
                metadata["cover"] = pics[0].data
        elif ext in (".m4a", ".mp4", ".aac"):
            audio = MP4(file_path)
            if audio.tags:
                metadata["title"] = audio.tags.get("\xa9nam", [None])[0]
                metadata["artist"] = audio.tags.get("\xa9ART", [None])[0]
                cover_list = audio.tags.get("covr")
                if cover_list:
                    metadata["cover"] = bytes(cover_list[0])
    except Exception as e:
        logger.warning(f"Metadata ajratishda xato: {e}")
    return metadata

def build_caption(title, artist, file_name):
    t = title or os.path.splitext(file_name)[0]
    a = artist or "Noma'lum ijrochi"
    return (
        f"🎵 <b>{t}</b>\n"
        f"🎤 <i>{a}</i>\n\n"
        f"🎧 Tinglang va zavqlaning!"
    )

def resize_cover(cover_bytes, max_size=1280):
    img = Image.open(io.BytesIO(cover_bytes))
    img.thumbnail((max_size, max_size))
    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=90)
    return buf.getvalue()

# =============================================
# BOT HANDLERLARI
# =============================================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🎵 <b>Musiqa Bot</b>\n\n"
        "Menga MP3, FLAC yoki M4A fayl yuboring — "
        "men uni avtomatik ravishda kanalga joylashtirib beraman.\n\n"
        "✅ Musiqa nomi va ijrochi rasmi bilan chiroyli formatda yuboriladi.",
        parse_mode="HTML",
    )

async def handle_audio(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if user.id != ADMIN_ID:
        await update.message.reply_text("❌ Sizda ruxsat yo'q.")
        return

    msg = update.message
    audio = msg.audio or msg.document
    if audio is None:
        await msg.reply_text("⚠️ Iltimos, audio fayl yuboring.")
        return

    status_msg = await msg.reply_text("⏳ Fayl yuklanmoqda...")
    file = await context.bot.get_file(audio.file_id)
    file_name = getattr(audio, "file_name", None) or "music.mp3"
    file_path = f"/tmp/{audio.file_unique_id}_{file_name}"
    await file.download_to_drive(file_path)

    await status_msg.edit_text("🔍 Metadata o'qilmoqda...")
    meta = extract_metadata(file_path)
    caption = build_caption(meta["title"], meta["artist"], file_name)

    await status_msg.edit_text("📤 Kanalga yuborilmoqda...")
    try:
        with open(file_path, "rb") as audio_file:
            if meta["cover"]:
                cover_io = io.BytesIO(resize_cover(meta["cover"]))
                cover_io.name = "cover.jpg"
                await context.bot.send_photo(
                    chat_id=CHANNEL_ID, photo=cover_io,
                    caption=caption, parse_mode="HTML",
                )
                audio_file.seek(0)
                await context.bot.send_audio(
                    chat_id=CHANNEL_ID, audio=audio_file,
                    title=meta["title"] or os.path.splitext(file_name)[0],
                    performer=meta["artist"] or "Noma'lum",
                )
            else:
                await context.bot.send_audio(
                    chat_id=CHANNEL_ID, audio=audio_file,
                    caption=caption, parse_mode="HTML",
                    title=meta["title"] or os.path.splitext(file_name)[0],
                    performer=meta["artist"] or "Noma'lum",
                )
        await status_msg.edit_text("✅ Musiqa kanalga muvaffaqiyatli yuborildi!")
    except Exception as e:
        logger.error(f"Xato: {e}")
        await status_msg.edit_text(f"❌ Xato: {e}")
    finally:
        if os.path.exists(file_path):
            os.remove(file_path)

# =============================================
# MAIN
# =============================================

async def run():
    await start_web_server()
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.AUDIO | filters.Document.AUDIO, handle_audio))

    logger.info("Bot ishga tushdi...")
    await app.initialize()
    await app.start()
    await app.updater.start_polling()

    await asyncio.Event().wait()

if __name__ == "__main__":
    asyncio.run(run())
