import os
import logging
from fastapi import FastAPI, Request
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.utils.media_group import MediaGroupBuilder
from aiogram.types import Update

# ============================================
# SIZNING TOKEN VA CHANNEL ID
# ============================================
BOT_TOKEN = "8799250450:AAHEZxCDTyECh840JFZ29LyGcRU5nwEB624"
CHANNEL_ID = "-1002199433054"  # String holatda

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Botni ishga tushirish
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
        "⚠️ **MUHIM:** Musiqa va rasmni **BIRGALIKDA** (bitta xabarda) yuboring!\n\n"
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
                    f"🆔 **ID:** {channel.id}\n"
                    f"👥 **A'zolar:** {channel.members_count if hasattr(channel, 'members_count') else 'Noma'lum'}")
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
        
        # Rasm uchun caption
        caption = (
            f"🎵 **{performer}** – {song_title}\n\n"
            f"📢 **Kanal:** {channel.title}\n"
            f"⏱ Davomiyligi: {audio.duration // 60}:{audio.duration % 60:02d}\n"
            f"💾 Hajmi: {audio.file_size / (1024*1024):.2f} MB"
        )
        
        # Rasm qo'shish (eng sifatli)
        photo = message.photo[-1]
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
        logger.error(f"Xatolik: {e}")
        await message.reply(f"❌ Xatolik: {str(e)}")

@dp.message(F.audio)
async def handle_audio_only(message: types.Message):
    audio = message.audio
    await message.reply(
        f"⚠️ **Faqat musiqa!**\n\n"
        f"Musiqa: {audio.title or 'Noma'lum'} - {audio.performer or 'Noma'lum'}\n\n"
        f"Iltimos, musiqa bilan birga **rasm** ham yuboring.",
        parse_mode="Markdown"
    )

@dp.message(F.photo)
async def handle_photo_only(message: types.Message):
    await message.reply(
        "⚠️ **Faqat rasm!**\n\n"
        "Iltimos, rasm bilan birga **musiqa (MP3)** ham yuboring.",
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
    else:
        logger.info("RAILWAY_PUBLIC_DOMAIN topilmadi, local rejim")

@app.on_event("shutdown")
async def on_shutdown():
    await bot.delete_webhook()
    await bot.session.close()
    logger.info("Bot to'xtadi")

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
