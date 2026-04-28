import os
import logging
from fastapi import FastAPI, Request
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.utils.media_group import MediaGroupBuilder
from aiogram.types import Update

# ============================================
# Environment variables (XAVFSIZ)
# ============================================
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID")

if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN environment variable not set!")

if not CHANNEL_ID:
    raise ValueError("CHANNEL_ID environment variable not set!")

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Bot
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()
app = FastAPI()

channel_info = None

async def get_channel_data():
    global channel_info
    if channel_info is None:
        try:
            channel_info = await bot.get_chat(CHANNEL_ID)
            logger.info(f"Kanalga ulandi: {channel_info.title}")
        except Exception as e:
            logger.error(f"Kanal xatosi: {e}")
            channel_info = None
    return channel_info

# ============ BUYRUQLAR ============
@dp.message(Command("start"))
async def start_command(message: types.Message):
    await message.answer(
        "🎵 **Musiqa botiga xush kelibsiz!**\n\n"
        "Botdan foydalanish:\n"
        "1. Musiqa (MP3) yuboring\n"
        "2. Rasm yuboring\n\n"
        "⚠️ **MUHIM:** Musiqa va rasmni BIRGALIKDA yuboring!\n\n"
        "✅ /info - kanal ma'lumoti",
        parse_mode="Markdown"
    )

@dp.message(Command("info"))
async def info_command(message: types.Message):
    try:
        channel = await get_channel_data()
        if channel:
            text = (f"📢 **Kanal ma'lumotlari:**\n"
                    f"📛 **Nomi:** {channel.title}\n"
                    f"🆔 **ID:** {channel.id}")
            await message.answer(text, parse_mode="Markdown")
        else:
            await message.answer("❌ Kanal topilmadi! Bot kanalda adminmi?")
    except Exception as e:
        await message.answer(f"❌ Xatolik: {str(e)}")

@dp.message(F.audio & F.photo)
async def handle_audio_with_photo(message: types.Message):
    try:
        channel = await get_channel_data()
        if not channel:
            await message.reply("❌ Kanal topilmadi!")
            return
            
        album_builder = MediaGroupBuilder()
        
        audio = message.audio
        song_title = audio.title if audio.title else "Noma'lum qo'shiq"
        performer = audio.performer if audio.performer else "Noma'lum ijrochi"
        
        # Davomiylikni hisoblash
        minutes = audio.duration // 60
        seconds = audio.duration % 60
        
        # Rasm uchun caption (f-string to'g'ri yopilgan)
        caption_text = f"🎵 {performer} – {song_title}\n\n📢 Kanal: {channel.title}\n⏱ Davomiyligi: {minutes}:{seconds:02d}"
        
        # Rasm qo'shish
        photo = message.photo[-1]
        album_builder.add_photo(
            media=photo.file_id,
            caption=caption_text,
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
            f"✅ Muvaffaqiyatli!\n\n🎵 {song_title} - {performer}\n📢 Kanalga yuborildi!",
            parse_mode="Markdown"
        )
        
    except Exception as e:
        logger.error(f"Xatolik: {e}")
        await message.reply(f"❌ Xatolik: {str(e)}")

@dp.message(F.audio)
async def handle_audio_only(message: types.Message):
    await message.reply(
        "⚠️ Faqat musiqa!\n\nIltimos, musiqa bilan birga rasm ham yuboring.",
        parse_mode="Markdown"
    )

@dp.message(F.photo)
async def handle_photo_only(message: types.Message):
    await message.reply(
        "⚠️ Faqat rasm!\n\nIltimos, rasm bilan birga musiqa ham yuboring.",
        parse_mode="Markdown"
    )

@dp.message()
async def handle_other(message: types.Message):
    await message.reply(
        "❓ Noto'g'ri format!\n\n✅ Musiqa + Rasm birgalikda\n✅ /start - boshlash\n✅ /info - kanal ma'lumoti",
        parse_mode="Markdown"
    )

# ============ WEBHOOK ============
@app.post("/webhook")
async def webhook(request: Request):
    try:
        update_data = await request.json()
        update = Update.model_validate(update_data, context={"bot": bot})
        await dp.feed_update(bot, update)
        return {"status": "ok"}
    except Exception as e:
        logger.error(f"Webhook xato: {e}")
        return {"status": "error", "message": str(e)}

@app.get("/")
async def root():
    return {
        "status": "active",
        "bot": "Music Bot",
        "channel_id": CHANNEL_ID
    }

@app.get("/health")
async def health():
    return {"status": "healthy"}

@app.on_event("startup")
async def on_startup():
    logger.info("Bot ishga tushmoqda...")
    
    # Test bot
    try:
        bot_info = await bot.get_me()
        logger.info(f"Bot: @{bot_info.username}")
    except Exception as e:
        logger.error(f"Bot xatosi: {e}")
    
    # Kanalni tekshirish
    try:
        channel = await bot.get_chat(CHANNEL_ID)
        logger.info(f"Kanal: {channel.title}")
    except Exception as e:
        logger.error(f"Kanal xatosi: {e}")
    
    # Webhook sozlash
    railway_domain = os.getenv("RAILWAY_PUBLIC_DOMAIN")
    if railway_domain:
        webhook_url = f"https://{railway_domain}/webhook"
        await bot.set_webhook(webhook_url)
        logger.info(f"Webhook sozlandi: {webhook_url}")

@app.on_event("shutdown")
async def on_shutdown():
    await bot.delete_webhook()
    await bot.session.close()
    logger.info("Bot to'xtadi")

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
