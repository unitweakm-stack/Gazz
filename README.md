# Telegram Channel Media Bot

Production-ready Telegram bot built with **Python + aiogram 3** for forwarding music and images to a Telegram channel.

## Features

- Accepts audio from users
- Validates incoming media type
- Republishes audio to your Telegram channel
- Sets audio **Title** in format: `KANAL_NOMI - IJROCHI`
- Sets audio **Performer** as channel name
- Uses **channel profile photo** as audio thumbnail automatically
- Falls back to `assets/default.jpg` if channel photo is missing
- Accepts images and posts them to the channel with caption = channel name
- Returns an error message for unsupported content types
- Async architecture with aiogram latest line
- Logging + try/except based error handling
- Clean service-oriented structure

---

## Project Structure

```bash
telegram_channel_music_bot/
├── app/
│   ├── handlers/
│   │   ├── common.py
│   │   └── media.py
│   ├── services/
│   │   ├── audio_processor.py
│   │   ├── channel_assets.py
│   │   └── media_publisher.py
│   ├── utils/
│   │   └── logging_setup.py
│   ├── __init__.py
│   └── config.py
├── assets/
│   └── default.jpg
├── main.py
├── requirements.txt
├── Procfile
├── .gitignore
└── README.md
```

---

## Configuration

Open `app/config.py` and set your real values:

```python
BOT_TOKEN = "PASTE_YOUR_BOT_TOKEN_HERE"
CHANNEL_ID = -1001234567890
```

> This project intentionally keeps `BOT_TOKEN` and `CHANNEL_ID` directly in code because that was your requirement. For public repositories, `.env` is safer.

---

## Local Installation

### 1) Clone the project

```bash
git clone <repo>
cd telegram_channel_music_bot
```

### 2) Create virtual environment

```bash
python -m venv .venv
source .venv/bin/activate
```

Windows:

```bash
.venv\Scripts\activate
```

### 3) Install dependencies

```bash
pip install -r requirements.txt
```

### 4) Run the bot

```bash
python main.py
```

---

## GitHub Push Commands

```bash
git init
git add .
git commit -m "init"
git branch -M main
git remote add origin <repo>
git push -u origin main
```

---

## Railway Deploy

### Deploy Steps

1. Open Railway dashboard
2. Click **New Project**
3. Select **Deploy from GitHub**
4. Connect your repository
5. Set **Start Command**:

```bash
python main.py
```

6. Deploy the project

### Important Note

This bot uses **long polling**, so Railway must keep the service running continuously. As long as the deployment is active, the bot will continue processing messages.

If Railway restarts the service, it will launch again automatically with the same start command.

---

## Telegram Channel Setup

### 1) Add bot as channel admin

In your channel:

- Open **Manage Channel**
- Go to **Administrators**
- Add your bot
- Give it permission to **Post Messages**

Without admin access, the bot cannot publish audio or images.

### 2) How to get `CHANNEL_ID`

Common format for channels:

```text
-100xxxxxxxxxx
```

Ways to get it:

- Add the bot to the channel as admin
- Forward any channel message to helper bots like `@userinfobot` and inspect the forwarded chat id
- Or create a temporary debug print with `getChat` and inspect your channel ID

---

## Testing Checklist

### Audio test

1. Start the bot in Telegram
2. Send an audio file or music
3. Bot should:
   - accept the audio
   - retag title as `KANAL_NOMI - IJROCHI`
   - set performer as channel name
   - use channel avatar or default thumbnail
   - post the audio into the channel

### Image test

1. Send a photo to the bot
2. Bot should post it to the channel
3. Caption should equal the channel name

### Validation test

1. Send text, sticker, video, or unsupported file
2. Bot should reply with an error message

---

## Technical Notes

- Supports Telegram `audio` and audio files sent as document
- Supports Telegram `photo` and image files sent as document
- MP3 and M4A metadata retagging is supported
- For unsupported audio containers, Telegram display metadata is still applied on send when possible
- Thumbnail is normalized to Telegram-friendly JPEG under size constraints

---

## Why this project is production-friendly

- Async/await everywhere
- Separation of concerns by handlers/services/utils
- Logging enabled
- Error-safe processing with graceful fallback
- Railway-ready structure
- Easy to maintain and extend

---

## Next improvements you can add later

- Admin-only usage restriction
- User statistics
- Database logging
- Duplicate media detection
- Auto-delete user messages after processing
- Webhook mode instead of polling

---

## Official References

- aiogram documentation: https://docs.aiogram.dev/
- SendAudio method: https://docs.aiogram.dev/en/latest/api/methods/send_audio.html
- Telegram Bot API: https://core.telegram.org/bots/api
- Railway start command docs: https://docs.railway.com/deployments/start-command
