import os

# Railway Environment Variables dan o'qiydi
# Agar u yerda topilmasa, default qiymatlarni oladi
BOT_TOKEN = os.environ.get("BOT_TOKEN", "YOUR_BOT_TOKEN_HERE")
CHANNEL_ID = os.environ.get("CHANNEL_ID", "@your_channel_username")

# ADMIN_ID doim raqam (int) bo'lishi kerak
try:
    ADMIN_ID = int(os.environ.get("ADMIN_ID", 123456789))
except (ValueError, TypeError):
    ADMIN_ID = 0 
