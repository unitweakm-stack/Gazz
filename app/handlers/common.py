from aiogram import Router
from aiogram.filters import CommandStart, Command
from aiogram.types import Message

router = Router(name=__name__)


@router.message(CommandStart())
async def start_handler(message: Message) -> None:
    await message.answer(
        "✅ Bot ishga tayyor.\n\n"
        "Menga audio yuboring — men uni kanalga title, performer va thumbnail bilan joylayman.\n"
        "Menga rasm yuboring — men uni ham kanalga caption bilan post qilaman."
    )


@router.message(Command("help"))
async def help_handler(message: Message) -> None:
    await message.answer(
        "ℹ️ Qo‘llab-quvvatlanadi:\n"
        "• Audio fayl yoki music\n"
        "• Rasm / photo\n\n"
        "❌ Video, sticker, voice, file va boshqa turlar qabul qilinmaydi."
    )
