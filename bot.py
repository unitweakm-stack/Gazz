import os
import logging
from fastapi import FastAPI, Request
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.utils.media_group import MediaGroupBuilder
from aiogram.types import Update

# Konfiguratsiya
TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID")

if not TOKEN or not CHANNEL_ID:
    raise ValueError("BOT_TOKEN va CHANNEL_ID environment variables sozlanmagan!")

# Bot va app sozlamalari
bot = Bot(token=TOKEN)
dp = Dispatcher()
app = FastAPI()

# Kanal ma'lumotlari
channel_info = None

async def get_channel_data():
    global channel_info
    if channel_info is None:
        channel_info = await bot.get_chat(CHANNEL_ID)
    return channel_info

# Handlerlar
@dp.message(Command("start"))
async def start_command(message: types.Message):
    await message.answer(
        "🎵 **Musiqa botiga xush kelibsiz!**\n\n"
        "Botdan foydalanish:\n"
        "1. Musiqa (MP3) yuboring\n"
        "2. Rasm yuboring\n\n"
        "⚠️ **MUHIM:** Musiqa va rasmni **BIRGALIKDA** (bitta xabarda) yuboring!",
        parse_mode="Markdown"
    )

@dp.message(Command("info"))
async def info_command(message: types.Message):
    try:
        channel = await get_channel_data()
        text = (f"📢 **Kanal ma'lumotlari:**\n"
                f"📛 **Nomi:** {channel.title}\n"
                f"🆔 **ID:** {channel.id}")
        await message.answer(text, parse_mode="Markdown")
    except Exception as e:
        await message.answer(f"❌ Xatolik: {str(e)}")

@dp.message(F.audio & F.photo)
async def handle_audio_with_photo(message: types.Message):
    try:
        channel = await get_channel_data()
        album_builder = MediaGroupBuilder()
        
        audio = message.audio
        song_title = audio.title if audio.title else "Noma'lum qo'shiq"
        performer = audio.performer if audio.performer else "Noma'lum ijrochi"
        
        # Rasm uchun caption
        caption = (
            f"🎵 **{performer}** – {song_title}\n\n"
            f"📢 **Kanal:** {channel.title}\n"
            f"⏱ Davomiyligi: {audio.duration // 60}:{audio.duration % 60:02d}\n"
            f"💾 Hajmi: {audio.file_size / (1024*1024):.2f} MB"
        )
        
        # Rasm qo'shish
        photo = message.photo[-1]  # Eng sifatli rasm
        album_builder.add_photo(
            media=photo.file_id,
            caption=caption,
            parse_mode="Markdown"
        )
        
        # Musiqa qo'shish
        album_builder.add_audio(
            media=audio.file_id,
            performer=performer,
            title=song_title
        )
        
        # Kanalga yuborish
        await bot.send_media_group(
            chat_id=CHANNEL_ID,
            media=album_builder.build()
        )
        
        await message.reply(
            f"✅ **Muvaffaqiyatli!**\n\n"
            f"🎵 {song_title} - {performer}\n"
            f"📢 Kanalga yuborildi!",
            parse_mode="Markdown"
        )
        
    except Exception as e:
        logging.error(f"Xatolik: {e}")
        await message.reply(f"❌ Xatolik: {str(e)}")

@dp.message(F.audio)
async def handle_audio_only(message: types.Message):
    await message.reply(
        "⚠️ **Faqat musiqa!**\n\n"
        "Iltimos, musiqa bilan birga **rasm** ham yuboring.",
        parse_mode="Markdown"
    )

@dp.message(F.photo)
async def handle_photo_only(message: types.Message):
    await message.reply(
        "⚠️ **Faqat rasm!**\n\n"
        "Iltimos, rasm bilan birga **musiqa** ham yuboring.",
        parse_mode="Markdown"
    )

@dp.message()
async def handle_other(message: types.Message):
    await message.reply(
        "❓ **Noto'g'ri format!**\n\n"
        "✅ Musiqa (MP3) + Rasm birgalikda\n"
        "✅ /start - boshlash\n"
        "✅ /info - kanal ma'lumoti",
        parse_mode="Markdown"
    )

# Webhook endpoint
@app.post("/webhook")
async def webhook(request: Request):
    """Telegram webhook endpoint"""
    try:
        update_data = await request.json()
        update = Update.model_validate(update_data, context={"bot": bot})
        await dp.feed_update(bot, update)
        return {"status": "ok"}
    except Exception as e:
        logging.error(f"Webhook error: {e}")
        return {"status": "error", "message": str(e)}

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "active",
        "bot": "Telegram Music Bot",
        "channel_id": CHANNEL_ID
    }

@app.get("/health")
async def health():
    """Health check for Railway"""
    return {"status": "healthy"}

# Botni ishga tushirish va webhook sozlash
@app.on_event("startup")
async def on_startup():
    """Bot ishga tushganda webhook sozlash"""
    webhook_url = os.getenv("RAILWAY_PUBLIC_DOMAIN")
    
    if webhook_url:
        webhook_url = f"https://{webhook_url}/webhook"
        await bot.set_webhook(webhook_url)
        logging.info(f"Webhook sozlandi: {webhook_url}")
    else:
        logging.warning("RAILWAY_PUBLIC_DOMAIN topilmadi")

@app.on_event("shutdown")
async def on_shutdown():
    """Bot to'xtaganda webhook o'chirish"""
    await bot.delete_webhook()
    await bot.session.close()
    logging.info("Bot to'xtadi")
