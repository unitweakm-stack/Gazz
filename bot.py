import asyncio
import logging
import os
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.utils.media_group import MediaGroupBuilder

# Configuratsiya
TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID")

bot = Bot(token=TOKEN)
dp = Dispatcher()
channel_info = None

async def get_channel_data():
    global channel_info
    if channel_info is None:
        channel_info = await bot.get_chat(CHANNEL_ID)
    return channel_info

@dp.message(Command("start"))
async def start_command(message: types.Message):
    await message.answer(
        "🎵 **Musiqa botiga xush kelibsiz!**\n\n"
        "Botdan foydalanish uchun:\n"
        "1. Musiqa fayli (MP3) yuboring\n"
        "2. Rasm (rasm yoki surat) yuboring\n\n"
        "⚠️ **MUHIM:** Musiqa va rasmni **birgalikda** (bitta xabarda) yuboring!",
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
        
        caption = (
            f"🎵 **{performer}** – {song_title}\n\n"
            f"📢 **Kanal:** {channel.title}\n"
            f"⏱ Davomiyligi: {audio.duration // 60}:{audio.duration % 60:02d}"
        )
        
        photo = message.photo[-1]
        album_builder.add_photo(
            media=photo.file_id,
            caption=caption,
            parse_mode="Markdown"
        )
        
        album_builder.add_audio(
            media=audio.file_id,
            performer=performer,
            title=song_title
        )
        
        await bot.send_media_group(
            chat_id=CHANNEL_ID,
            media=album_builder.build()
        )
        
        await message.reply(
            f"✅ **Muvaffaqiyatli yuborildi!**\n\n"
            f"🎵 {song_title} - {performer}",
            parse_mode="Markdown"
        )
        
    except Exception as e:
        logging.error(f"Xatolik: {e}")
        await message.reply(f"❌ Xatolik: {str(e)}")

@dp.message(F.audio)
async def handle_audio_only(message: types.Message):
    await message.reply(
        "⚠️ **Faqat musiqa yubordingiz!**\n\n"
        "Musiqa bilan birga **rasm** ham yuboring.",
        parse_mode="Markdown"
    )

@dp.message(F.photo)
async def handle_photo_only(message: types.Message):
    await message.reply(
        "⚠️ **Faqat rasm yubordingiz!**\n\n"
        "Rasm bilan birga **musiqa** ham yuboring.",
        parse_mode="Markdown"
    )

@dp.message()
async def handle_other(message: types.Message):
    await message.reply(
        "❓ **Noto'g'ri format!**\n\n"
        "Faqat: Musiqa (MP3) + Rasm birgalikda\n"
        "/start - boshlash\n"
        "/info - kanal ma'lumoti",
        parse_mode="Markdown"
    )

async def main():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    await bot.delete_webhook(drop_pending_updates=True)
    print("🤖 Bot ishga tushdi...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
