from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from config import API_ID, API_HASH, BOT_TOKEN
import asyncio
import os

app = Client("cloner_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# Memory storage
USER_STATE = {}
SUDO_USERS = set()
THUMBNAIL_URL = {}
TARGET_CHANNEL = {}
WATERMARK_TEXT = {}

DEFAULT_SLEEP = [3, 5, 8, 13, 21, 32]  # exponential sleep fallback

def is_sudo(user_id):
    return user_id in SUDO_USERS

@app.on_message(filters.command("start"))
async def start(client, message):
    await message.reply_text(
        "Welcome! This bot can clone messages to your target channel with watermark/thumbnail.\n\n"
        "**Commands:**\n"
        "`/setchannel` - Set target channel ID\n"
        "`/setthumb` - Set thumb URL or watermark\n"
        "`/d` - Reset to default thumbnail\n"
        "`/id` - Get ID\n"
        "`/clone <start-end>` or forward messages directly",
        quote=True
    )

@app.on_message(filters.command("id"))
async def get_id(client, message):
    await message.reply_text(f"Your ID: `{message.from_user.id}`\nChat ID: `{message.chat.id}`", quote=True)

@app.on_message(filters.command("setchannel"))
async def set_channel(client, message):
    if not is_sudo(message.from_user.id):
        return await message.reply("You are not authorized.")
    USER_STATE[message.from_user.id] = "waiting_channel"
    await message.reply("Send the target channel ID (e.g., -1001234567890) or `/d` to clone personally.")

@app.on_message(filters.command("setthumb"))
async def set_thumb(client, message):
    if not is_sudo(message.from_user.id):
        return await message.reply("You are not authorized.")
    USER_STATE[message.from_user.id] = "waiting_thumb"
    await message.reply(
        "Send thumbnail URL or send plain text (like Admin) for watermark.\n\nUse `/d` to reset permanently."
    )

@app.on_message(filters.command("d"))
async def reset_thumb(client, message):
    if not is_sudo(message.from_user.id):
        return await message.reply("You are not authorized.")
    uid = message.from_user.id
    THUMBNAIL_URL.pop(uid, None)
    WATERMARK_TEXT.pop(uid, None)
    await message.reply("Thumbnail/watermark removed. Default Telegram behavior restored.")

@app.on_message(filters.command("addsudo"))
async def add_sudo(client, message):
    if message.from_user.id != message.from_user.id:
        return
    if len(message.command) < 2:
        return await message.reply("Usage: /addsudo <user_id>")
    try:
        SUDO_USERS.add(int(message.command[1]))
        await message.reply("SUDO user added.")
    except:
        await message.reply("Invalid ID.")

@app.on_message(filters.text & filters.private)
async def handle_input(client, message: Message):
    uid = message.from_user.id
    if not is_sudo(uid):
        return await message.reply("You are not authorized.")

    if USER_STATE.get(uid) == "waiting_channel":
        if message.text.strip() == "/d":
            TARGET_CHANNEL[uid] = None
            await message.reply("Now cloning personally.")
        else:
            try:
                TARGET_CHANNEL[uid] = int(message.text.strip())
                await message.reply(f"Target channel set to `{TARGET_CHANNEL[uid]}`.")
            except:
                await message.reply("Invalid channel ID.")
        USER_STATE.pop(uid)

    elif USER_STATE.get(uid) == "waiting_thumb":
        if message.text.strip() == "/d":
            THUMBNAIL_URL.pop(uid, None)
            WATERMARK_TEXT.pop(uid, None)
            await message.reply("Thumbnail reset to default.")
        elif message.text.startswith("http"):
            THUMBNAIL_URL[uid] = message.text.strip()
            WATERMARK_TEXT.pop(uid, None)
            await message.reply("Thumbnail set from URL.")
        else:
            WATERMARK_TEXT[uid] = message.text.strip()
            THUMBNAIL_URL.pop(uid, None)
            await message.reply(f"Watermark set: {message.text.strip()}")
        USER_STATE.pop(uid)

@app.on_message(filters.command("clone"))
async def clone_range(client, message):
    if not is_sudo(message.from_user.id):
        return await message.reply("You are not authorized.")
    args = message.text.split(" ")
    if len(args) != 2 or '-' not in args[1]:
        return await message.reply("Usage: /clone 1-100")
    start, end = map(int, args[1].split('-'))
    uid = message.from_user.id
    dest = TARGET_CHANNEL.get(uid, uid)

    for msg_id in range(start, end + 1):
        try:
            msg = await client.get_messages(message.chat.id, msg_id)
            await forward_media(client, msg, uid, dest)
            await asyncio.sleep(3)  # safe delay
        except Exception as e:
            await message.reply(f"Error forwarding message {msg_id}: {e}")
            await asyncio.sleep(DEFAULT_SLEEP[min(msg_id - start, len(DEFAULT_SLEEP)-1)])

@app.on_message(filters.media & filters.private)
async def forward_single(client, message):
    if not is_sudo(message.from_user.id):
        return await message.reply("You are not authorized.")
    uid = message.from_user.id
    dest = TARGET_CHANNEL.get(uid, uid)
    await forward_media(client, message, uid, dest)

async def forward_media(client, message, uid, dest):
    caption = message.caption or ""
    if uid in WATERMARK_TEXT:
        caption += f"\n\n⚠️ {WATERMARK_TEXT[uid]}"

    try:
        if message.video:
            await client.send_video(
                dest, video=message.video.file_id,
                caption=caption, thumb=THUMBNAIL_URL.get(uid)
            )
        elif message.photo:
            await client.send_photo(
                dest, photo=message.photo.file_id,
                caption=caption
            )
        elif message.document:
            await client.send_document(
                dest, document=message.document.file_id,
                caption=caption, thumb=THUMBNAIL_URL.get(uid)
            )
        else:
            await message.copy(dest)
    except Exception as e:
        await client.send_message(uid, f"Failed: {e}")

app.run()
