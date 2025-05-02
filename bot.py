import os
import asyncio
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from flask import Flask
from threading import Thread

# ================= FLASK HEALTH SERVER =================
app = Flask(__name__)

@app.route('/')
def health_check():
    return "OK", 200

def run_health_server():
    app.run(host='0.0.0.0', port=8080)

Thread(target=run_health_server).start()

# ================= BOT CONFIG =================
API_ID = int(os.environ.get("API_ID"))
API_HASH = os.environ.get("API_HASH")
BOT_TOKEN = os.environ.get("BOT_TOKEN")
ADMIN_ID = int(os.environ.get("ADMIN_ID", 0))

bot = Client("forward_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# ================= START HANDLER =================
@bot.on_message(filters.command("start") & filters.private)
async def start(client: Client, message: Message):
    name = message.from_user.first_name or "User"

    text = f"""ʜɪ {name}

ɪ'ᴍ ᴀ ᴀᴅᴠᴀɴᴄᴇᴅ ꜰᴏʀᴡᴀʀᴅ ʙᴏᴛ  
ɪ ᴄᴀɴ ꜰᴏʀᴡᴀʀᴅ ᴀʟʟ ᴍᴇssᴀɢᴇꜱ ꜰʀᴏᴍ ᴏɴᴇ ᴄʜᴀɴɴᴇʟ ᴛᴏ ᴀɴᴏᴛʜᴇʀ ᴄʜᴀɴɴᴇʟ

ᴄʟɪᴄᴋ ʜᴇʟᴘ ʙᴜᴛᴛᴏɴ ᴛᴏ ᴋɴᴏᴡ ᴍᴏʀᴇ ᴀʙᴏᴜᴛ ᴍᴇ"""

    buttons = InlineKeyboardMarkup([
        [InlineKeyboardButton("❣️ DEVELOPER ❣️", url="https://t.me/YourDeveloper")],
        [InlineKeyboardButton("🔍 SUPPORT GROUP", url="https://t.me/YourSupportGroup"),
         InlineKeyboardButton("🤖 UPDATE CHANNEL", url="https://t.me/YourUpdateChannel")],
        [InlineKeyboardButton("💝 SUBSCRIBE MY YOUTUBE CHANNEL", url="https://youtube.com/@YourChannel")],
        [InlineKeyboardButton("👩‍💻 HELP", callback_data="help"),
         InlineKeyboardButton("🧑‍🏫 ABOUT", callback_data="about")],
        [InlineKeyboardButton("⚙️ SETTINGS", callback_data="settings")]
    ])

    await message.reply(text, reply_markup=buttons)

# ================= CALLBACK HANDLERS =================
@bot.on_callback_query(filters.regex("help"))
async def help_cb(client, callback):
    await callback.answer("ℹ️ Help menu coming soon!", show_alert=True)

@bot.on_callback_query(filters.regex("about"))
async def about_cb(client, callback):
    await callback.answer("👤 Made by Developer", show_alert=True)

@bot.on_callback_query(filters.regex("settings"))
async def settings_cb(client, callback):
    await callback.answer("⚙️ Settings not available yet.", show_alert=True)

# ================= RUN BOT =================
print("✅ Bot is running with health check server on port 8080...")
bot.run()
