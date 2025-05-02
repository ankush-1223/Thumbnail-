from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext, MessageHandler, Filters
from telethon import TelegramClient
import logging
from other import clone_range, clone_full_channel, reset_thumbnail, watermark_video, edit_caption
import os

# Set up logging
logging.basicConfig(level=logging.INFO)

API_ID = os.getenv("API_ID")  # Environment variable for API_ID
API_HASH = os.getenv("API_HASH")  # Environment variable for API_HASH
BOT_TOKEN = os.getenv("BOT_TOKEN")  # Environment variable for BOT_TOKEN

# Initialize the Telegram bot
updater = Updater(BOT_TOKEN, use_context=True)
dispatcher = updater.dispatcher

# Telethon client for interacting with the channels
client = TelegramClient('bot_session', API_ID, API_HASH)

# /start command handler
def start(update: Update, context: CallbackContext):
    update.message.reply_text("Welcome! I can help you clone channels, modify thumbnails, and more. Use /help to get a list of commands.")

# /help command handler
def help_command(update: Update, context: CallbackContext):
    help_text = """
    Here are the available commands:
    /start - Welcome message
    /clone_range - Clone a specific range of messages from a source channel
    /clone_full_channel - Clone the entire content of a source channel
    /reset_thumbnail - Reset thumbnail to default
    /watermark_video - Add watermark to video
    /edit_caption - Edit captions on messages
    """
    update.message.reply_text(help_text)

# Command handlers
def clone_range_command(update: Update, context: CallbackContext):
    update.message.reply_text("Please send the link of the first message in the source channel.")
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, clone_range))

def clone_full_channel_command(update: Update, context: CallbackContext):
    update.message.reply_text("Please send the link of the last message from the source channel.")
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, clone_full_channel))

def reset_thumbnail_command(update: Update, context: CallbackContext):
    update.message.reply_text("Resetting thumbnails to default. This may take some time.")
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, reset_thumbnail))

def watermark_video_command(update: Update, context: CallbackContext):
    update.message.reply_text("Please send the watermark text to be added to the video.")
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, watermark_video))

def edit_caption_command(update: Update, context: CallbackContext):
    update.message.reply_text("Please send the new caption text you want to set.")
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, edit_caption))

# Add handlers to the dispatcher
dispatcher.add_handler(CommandHandler('start', start))
dispatcher.add_handler(CommandHandler('help', help_command))
dispatcher.add_handler(CommandHandler('clone_range', clone_range_command))
dispatcher.add_handler(CommandHandler('clone_full_channel', clone_full_channel_command))
dispatcher.add_handler(CommandHandler('reset_thumbnail', reset_thumbnail_command))
dispatcher.add_handler(CommandHandler('watermark_video', watermark_video_command))
dispatcher.add_handler(CommandHandler('edit_caption', edit_caption_command))

# Start the bot
updater.start_polling()
updater.idle()
