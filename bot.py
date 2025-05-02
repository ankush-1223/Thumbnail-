import os
import sys
import time
import asyncio
from threading import Thread
from flask import Flask
from pyrogram import Client, filters, idle
from pyrogram.types import (
    Message, InlineKeyboardMarkup,
    InlineKeyboardButton, CallbackQuery
)

# ==================== FLASK SERVER ====================
app = Flask(__name__)

@app.route('/')
def health_check():
    return "BOT_IS_ALIVE", 200

def run_flask():
    app.run(host='0.0.0.0', port=8080)

# ==================== BOT CONFIGURATION ====================
class Config:
    # Required (from Keyob environment)
    API_ID = int(os.environ["API_ID"])
    API_HASH = os.environ["API_HASH"]
    BOT_TOKEN = os.environ["BOT_TOKEN"]
    ADMIN_ID = int(os.environ["ADMIN_ID"])
    
    # Configurable via bot
    SUDO_USERS = []
    TARGET_CHAT = ""
    SOURCE_CHAT = ""
    SKIP_MSG = 0
    FLOOD_DELAY = 32  # seconds
    CLONING_ACTIVE = False
    STATUS_MSG = None
    CURRENT_SETTING = None  # Track which setting is being configured
    
    # Statistics
    stats = {
        'total': 0,
        'forwarded': 0,
        'skipped': 0,
        'errors': 0
    }

# ==================== BOT SETUP ====================
bot = Client(
    "UltimateCloner",
    api_id=Config.API_ID,
    api_hash=Config.API_HASH,
    bot_token=Config.BOT_TOKEN,
    workers=100
)

# ==================== UTILITIES ====================
def is_admin(user_id):
    return user_id == Config.ADMIN_ID or user_id in Config.SUDO_USERS

async def update_status():
    """Update progress message"""
    while Config.CLONING_ACTIVE:
        total_effective = max(1, Config.stats['total'] - Config.SKIP_MSG)
        progress = (Config.stats['forwarded'] / total_effective) * 100
        
        text = (
            "🔄 **Cloning Progress**\n\n"
            f"• Total: `{Config.stats['total']}`\n"
            f"• Forwarded: `{Config.stats['forwarded']}`\n"
            f"• Skipped: `{Config.stats['skipped']}`\n"
            f"• Errors: `{Config.stats['errors']}`\n"
            f"• Progress: `{progress:.2f}%`\n\n"
            f"⏳ Delay: `{Config.FLOOD_DELAY}s`"
        )
        
        try:
            if Config.STATUS_MSG:
                await Config.STATUS_MSG.edit(text)
            await asyncio.sleep(5)
        except Exception as e:
            print(f"Status error: {e}")

# ==================== COMMAND HANDLERS ====================
@bot.on_message(filters.command("start") & filters.private)
async def start_cmd(client, message):
    if not is_admin(message.from_user.id):
        await message.reply("🚫 Unauthorized!")
        return

    buttons = InlineKeyboardMarkup([
        [InlineKeyboardButton("⚙️ Setup", callback_data="setup_menu")],
        [InlineKeyboardButton("🚀 Start Cloning", callback_data="start_clone")]
    ])
    
    await message.reply(
        f"🤖 **Ultimate Cloner**\n\n"
        f"👑 Owner: `{Config.ADMIN_ID}`\n"
        f"📊 Status: `{'✅ Ready' if not Config.CLONING_ACTIVE else '🔄 Cloning'}`\n"
        f"⏱ Delay: `{Config.FLOOD_DELAY}s`\n\n"
        f"▫️ Target: `{Config.TARGET_CHAT or 'Not set'}`\n"
        f"▫️ Source: `{Config.SOURCE_CHAT or 'Not set'}`",
        reply_markup=buttons
    )

# ==================== SETUP MENU ====================
@bot.on_callback_query(filters.regex("^setup_menu$"))
async def setup_menu(client, query):
    buttons = InlineKeyboardMarkup([
        [InlineKeyboardButton("🎯 Set Target", callback_data="set_target")],
        [InlineKeyboardButton("🔗 Set Source", callback_data="set_source")],
        [InlineKeyboardButton("⏱ Set Delay", callback_data="set_delay")],
        [InlineKeyboardButton("🔙 Back", callback_data="main_menu")]
    ])
    
    await query.message.edit(
        "⚙️ **Bot Setup Menu**\n\n"
        "Configure your cloning settings:",
        reply_markup=buttons
    )

# ==================== SETUP HANDLERS ====================
@bot.on_callback_query(filters.regex("^set_"))
async def setup_handler(client, query):
    if query.data == "set_target":
        Config.CURRENT_SETTING = "target"
        await query.message.edit("📢 Send me the target channel username or ID:")
        
    elif query.data == "set_source":
        Config.CURRENT_SETTING = "source"
        await query.message.edit("🔗 Send me the source channel username or ID:")
        
    elif query.data == "set_delay":
        Config.CURRENT_SETTING = "delay"
        await query.message.edit("⏱ Send me the delay between forwards (in seconds):")

@bot.on_message(filters.private & filters.text & ~filters.command("start"))
async def handle_setting_input(client, message):
    if not is_admin(message.from_user.id):
        return
        
    if Config.CURRENT_SETTING == "target":
        Config.TARGET_CHAT = message.text.strip()
        await message.reply(f"✅ Target set to: `{Config.TARGET_CHAT}`")
        
    elif Config.CURRENT_SETTING == "source":
        Config.SOURCE_CHAT = message.text.strip()
        await message.reply(f"✅ Source set to: `{Config.SOURCE_CHAT}`")
        
    elif Config.CURRENT_SETTING == "delay":
        try:
            Config.FLOOD_DELAY = int(message.text.strip())
            await message.reply(f"✅ Delay set to: `{Config.FLOOD_DELAY}s`")
        except ValueError:
            await message.reply("❌ Please send a valid number")
            
    Config.CURRENT_SETTING = None

# ==================== CLONING SYSTEM ====================
async def clone_messages():
    Config.CLONING_ACTIVE = True
    Config.STATUS_MSG = await bot.send_message(
        Config.ADMIN_ID,
        "🔄 Starting cloning process..."
    )
    asyncio.create_task(update_status())
    
    try:
        async for msg in bot.get_chat_history(Config.SOURCE_CHAT):
            if not Config.CLONING_ACTIVE:
                break
                
            Config.stats['total'] += 1
            
            if Config.stats['total'] <= Config.SKIP_MSG:
                Config.stats['skipped'] += 1
                continue
                
            try:
                await bot.copy_message(
                    chat_id=Config.TARGET_CHAT,
                    from_chat_id=Config.SOURCE_CHAT,
                    message_id=msg.id
                )
                Config.stats['forwarded'] += 1
                await asyncio.sleep(Config.FLOOD_DELAY)
            except Exception as e:
                Config.stats['errors'] += 1
                print(f"Clone error: {e}")
                
    finally:
        Config.CLONING_ACTIVE = False
        await Config.STATUS_MSG.edit(
            f"✅ **Completed**\n\n"
            f"Forwarded: `{Config.stats['forwarded']}`\n"
            f"Errors: `{Config.stats['errors']}`"
        )

# ==================== CALLBACK HANDLERS ====================
@bot.on_callback_query(filters.regex("^start_clone$"))
async def start_cloning(client, query):
    if Config.CLONING_ACTIVE:
        await query.answer("Already cloning!", show_alert=True)
        return
        
    if not all([Config.TARGET_CHAT, Config.SOURCE_CHAT]):
        await query.answer("Set target/source first!", show_alert=True)
        return
        
    await query.answer("Starting clone job...")
    asyncio.create_task(clone_messages())

@bot.on_callback_query(filters.regex("^main_menu$"))
async def main_menu(client, query):
    await start_cmd(client, query.message)

# ==================== MAIN ====================
async def run_bot():
    await bot.start()
    print(f"""
╔══════════════════════╗
║   ULTIMATE CLONER    ║
╠══════════════════════╣
║ • Admin: {Config.ADMIN_ID}
║ • Version: 2.4
╚══════════════════════╝
""")
    await idle()

if __name__ == "__main__":
    # Start Flask server in separate thread
    flask_thread = Thread(target=run_flask)
    flask_thread.daemon = True
    flask_thread.start()

    # Run the bot
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(run_bot())
    except KeyboardInterrupt:
        print("\nBot stopped manually")
    except Exception as e:
        print(f"Fatal error: {e}")
    finally:
        if bot.is_connected:
            loop.run_until_complete(bot.stop())
        loop.close()
