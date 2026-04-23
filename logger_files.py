import os
import datetime
import asyncio
from pathlib import Path

LOGS_DIR = "logs"
PHOTOS_DIR = "logs/photos"
MESSAGES_FILE = "logs/messages.txt"
USERS_FILE = "logs/users.txt"

# Локи для файлов
_messages_lock = asyncio.Lock()
_users_lock = asyncio.Lock()
_photos_lock = asyncio.Lock()

def init_logs():
    os.makedirs(LOGS_DIR, exist_ok=True)
    os.makedirs(PHOTOS_DIR, exist_ok=True)
    if not os.path.exists(MESSAGES_FILE):
        with open(MESSAGES_FILE, "w", encoding="utf-8") as f:
            f.write("=== ЛОГА СООБЩЕНИЙ ===\n\n")
    if not os.path.exists(USERS_FILE):
        with open(USERS_FILE, "w", encoding="utf-8") as f:
            f.write("=== БАЗА ПОЛЬЗОВАТЕЛЕЙ ===\n\n")

async def log_message(user_id, username, first_name="", text="", msg_type="text"):
    init_logs()
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{now}] [{msg_type.upper()}] user_id={user_id} | @{username} | {first_name}\n{text}\n{'-'*60}\n"
    async with _messages_lock:
        with open(MESSAGES_FILE, "a", encoding="utf-8") as f:
            f.write(line)

async def log_photo(user_id, username, first_name="", photo_bytes=b"", caption=""):
    init_logs()
    now = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    filename = f"{PHOTOS_DIR}/{now}_uid{user_id}.jpg"
    async with _photos_lock:
        with open(filename, "wb") as f:
            f.write(photo_bytes)
    await log_message(user_id, username, first_name, f"[ФОТО] caption={caption} файл={filename}", msg_type="photo")
    return filename

async def log_user(user_id, username, first_name, last_name=""):
    init_logs()
    async with _users_lock:
        with open(USERS_FILE, "r", encoding="utf-8") as f:
            content = f.read()
        if f"user_id={user_id}" not in content:
            now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            line = f"[{now}] user_id={user_id} | @{username} | {first_name} {last_name}\n"
            with open(USERS_FILE, "a", encoding="utf-8") as f:
                f.write(line)
VOICE_DIR = "logs/voice"
CIRCLES_DIR = "logs/circles"

async def log_voice(user_id, username, first_name="", voice_bytes=b""):
    init_logs()
    os.makedirs(VOICE_DIR, exist_ok=True)
    now = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    filename = f"{VOICE_DIR}/{now}_uid{user_id}.ogg"
    async with _photos_lock:
        with open(filename, "wb") as f:
            f.write(voice_bytes)
    await log_message(user_id, username, first_name, f"[ГОЛОСОВОЕ] файл={filename}", msg_type="voice")
    return filename

async def log_circle(user_id, username, first_name="", circle_bytes=b""):
    init_logs()
    os.makedirs(CIRCLES_DIR, exist_ok=True)
    now = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    filename = f"{CIRCLES_DIR}/{now}_uid{user_id}.mp4"
    async with _photos_lock:
        with open(filename, "wb") as f:
            f.write(circle_bytes)
    await log_message(user_id, username, first_name, f"[КРУЖОЧЕК] файл={filename}", msg_type="circle")
    return filename