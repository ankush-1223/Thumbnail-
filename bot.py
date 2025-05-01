import os
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from utils import clean_caption, get_footer, get_thumbnail
from config import Config

bot = Client("CloneBot", api_id=Config.API_ID, api_hash=Config.API_HASH, bot_token=Config.BOT_TOKEN)

MAIN_CHANNEL = Config.MAIN_CHANNEL
ADMIN = int(Config.ADMIN_ID)

@bot.on_message(filters.command("start") & filters.private)
async def start(client, message):
    if message.from_user.id != ADMIN:
        return await message.reply("This bot is private.")
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("Set Main Channel", callback_data="set_main")],
        [InlineKeyboardButton("Set Thumbnail URL", callback_data="set_thumb")]
    ])
    await message.reply("Welcome to Clone Bot!", reply_markup=keyboard)

@bot.on_callback_query()
async def callback(bot, query):
    if query.from_user.id != ADMIN:
        return await query.answer("Not for you.", show_alert=True)
    if query.data == "set_main":
        await query.message.reply("Send the @username or ID of the target channel.")
    elif query.data == "set_thumb":
        await query.message.reply("Send the thumbnail URL.")

@bot.on_message(filters.private & filters.text)
async def handle_input(client, message):
    global MAIN_CHANNEL
    if message.from_user.id != ADMIN:
        return
    if message.text.startswith("@") or message.text.isdigit():
        MAIN_CHANNEL = message.text.strip()
        await message.reply(f"Main channel set to: {MAIN_CHANNEL}")
    elif message.text.startswith("http"):
        with open("thumbnail.txt", "w") as f:
            f.write(message.text.strip())
        await message.reply("Thumbnail URL updated.")

@bot.on_message(filters.channel)
async def forward_message(bot, message):
    if not MAIN_CHANNEL:
        return
    thumb = get_thumbnail()
    caption = clean_caption(message.caption or "")
    footer = get_footer()
    media = message.video or message.photo or message.document
    if media:
        await bot.copy_message(chat_id=MAIN_CHANNEL, from_chat_id=message.chat.id,
                               message_id=message.id,
                               caption=f"{caption}

{footer}",
                               thumb=thumb)

bot.run()
