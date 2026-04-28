import os

# Railway da Environment Variables ishlatiladi (config.py dan emas)

# Lekin lokal test uchun default qiymatlar shu yerda

BOT_TOKEN = os.environ.get(“BOT_TOKEN”, “YOUR_BOT_TOKEN_HERE”)
CHANNEL_ID = os.environ.get(“CHANNEL_ID”, “@your_channel_username”)
ADMIN_ID = int(os.environ.get(“ADMIN_ID”, “123456789”))
