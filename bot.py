# Line 1–5: Flask server to pass health check
# Line 1–5: Flask server to pass health check
from flask import Flask
import threading

web_app = Flask('')

@web_app.route('/')
def home():
    return "Bot is running!"

def run_web():
    web_app.run(host='0.0.0.0', port=8080)

threading.Thread(target=run_web).start()

# Pyrogram and core libraries
from pyrogram import Client, filters, types
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from config import API_ID, API_HASH, BOT_TOKEN, OWNER_ID
import os
import asyncio

# Pyrogram Bot App Initialization
app = Client("bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# Global variables
sudo_users = set()
target_channel = None
default_thumb = None

Buttons UI

def main_menu(): return InlineKeyboardMarkup([ [ InlineKeyboardButton("Set Channel", callback_data="set_channel"), InlineKeyboardButton("Set Thumbnail", callback_data="set_thumb") ], [ InlineKeyboardButton("Reset Thumbnail", callback_data="reset_thumb"), InlineKeyboardButton("Add Sudo", callback_data="add_sudo") ], [ InlineKeyboardButton("Help", callback_data="help") ] ])

@app.on_message(filters.command("start") & filters.private) async def start(client, message): await message.reply_text( "Welcome! Clone to target channel with watermark/thumbnail.", reply_markup=main_menu() )

@app.on_message(filters.command("id") & filters.private) async def get_id(client, message): await message.reply_text(f"Your ID: {message.from_user.id}")

@app.on_callback_query() async def callback_handler(client, callback_query): data = callback_query.data user_id = callback_query.from_user.id

if data == "set_channel":
    await callback_query.message.edit("Send the Channel ID (or /d to use personally):")
    app.set_channel_user = user_id

elif data == "set_thumb":
    await callback_query.message.edit("Send thumbnail URL or text for watermark:")
    app.set_thumb_user = user_id

elif data == "reset_thumb":
    global default_thumb
    default_thumb = None
    await callback_query.message.edit("Thumbnail removed permanently. Back to default.")

elif data == "add_sudo":
    await callback_query.message.edit("Send User ID to add as sudo:")
    app.add_sudo_user = user_id

elif data == "help":
    await callback_query.message.edit(
        "This bot clones messages/media to your channel with thumbnail or watermark.\n\n"
        "/start - Show menu\n"
        "/id - Get your Telegram ID\n"
        "Clone: Forward any message here.\n\n"
        "Control via buttons.",
        reply_markup=main_menu()
    )

@app.on_message(filters.private) async def handle_input(client, message): user_id = message.from_user.id global target_channel, default_thumb

if getattr(app, 'set_channel_user', None) == user_id:
    channel = message.text.strip()
    if channel == "/d":
        target_channel = None
        await message.reply("Personal use selected. No channel set.")
    else:
        target_channel = channel
        await message.reply(f"Channel ID set to: `{channel}`")
    app.set_channel_user = None

elif getattr(app, 'set_thumb_user', None) == user_id:
    input_text = message.text.strip()
    if input_text.startswith("http"):
        default_thumb = input_text
        await message.reply("Thumbnail URL set.")
    else:
        default_thumb = f"WATERMARK:{input_text}"
        await message.reply("Watermark text set.")
    app.set_thumb_user = None

elif getattr(app, 'add_sudo_user', None) == user_id:
    try:
        new_id = int(message.text.strip())
        sudo_users.add(new_id)
        await message.reply(f"Added `{new_id}` to sudo users.")
    except:
        await message.reply("Invalid ID")
    app.add_sudo_user = None

elif message.forward_from_chat or message.forward_from:
    if user_id == OWNER_ID or user_id in sudo_users:
        await clone_message(message)
    else:
        await message.reply("You are not allowed to clone messages.")

async def clone_message(message): global target_channel, default_thumb media = message.media caption = message.caption or ""

# Apply watermark if needed
if default_thumb and default_thumb.startswith("WATERMARK:"):
    watermark = default_thumb.split(":", 1)[1]
    caption = f"{caption}\n\nWatermark: {watermark}"

try:
    # Forwarding/Cloning logic
    await asyncio.sleep(32)  # flood wait safe timer
    await app.copy_message(
        chat_id=target_channel if target_channel else message.from_user.id,
        from_chat_id=message.chat.id,
        message_id=message.id,
        caption=caption if caption else None
    )
except Exception as e:
    await message.reply(f"Error: {e}")

if name == "main": app.run()
