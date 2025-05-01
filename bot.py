#!/usr/bin/env python3
import os
import sys
import time
import asyncio
from typing import List, Dict, Optional
from pyrogram import Client, filters, idle
from pyrogram.types import (
    Message, InlineKeyboardMarkup,
    InlineKeyboardButton, CallbackQuery
)

# ==================== CONFIGURATION ====================
class Config:
    # Required (set in Keyob environment)
    API_ID = int(os.environ["API_ID"])
    API_HASH = os.environ["API_HASH"]
    BOT_TOKEN = os.environ["BOT_TOKEN"]
    ADMIN_ID = int(os.environ["ADMIN_ID"])
    
    # Optional (configurable via bot)
    SUDO_USERS: List[int] = []
    TARGET_CHAT: str = ""
    SOURCE_CHAT: str = ""
    SKIP_MSG: int = 0
    FLOOD_DELAY: int = 32  # seconds
    CLONING_ACTIVE: bool = False
    STATUS_MSG: Optional[Message] = None
    
    # Statistics
    stats: Dict[str, int] = {
        'total': 0,
        'forwarded': 0,
        'skipped': 0,
        'errors': 0
    }

# ==================== HEALTH CHECK ====================
def handle_health_check():
    """Handle Keyob health check requests"""
    if any(arg in sys.argv for arg in ["--health-check", "healthcheck"]):
        print("HEALTH_CHECK_OK")
        sys.exit(0)

handle_health_check()  # Exit immediately if health check

# ==================== BOT SETUP ====================
bot = Client(
    name="UltimateCloner",
    api_id=Config.API_ID,
    api_hash=Config.API_HASH,
    bot_token=Config.BOT_TOKEN,
    workers=100,
    sleep_threshold=60
)

# ==================== UTILITIES ====================
def is_admin(user_id: int) -> bool:
    """Check if user is admin or sudo"""
    return user_id == Config.ADMIN_ID or user_id in Config.SUDO_USERS

async def health_ping():
    """Prevent instance shutdown"""
    while True:
        print(f"🫀 Health ping at {time.strftime('%H:%M:%S')}")
        await asyncio.sleep(300)  # Every 5 minutes

async def update_status():
    """Update progress message"""
    while Config.CLONING_ACTIVE:
        progress = (Config.stats['forwarded'] / 
                  max(1, (Config.stats['total'] - Config.SKIP_MSG)) * 100
        
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
            print(f"Status update error: {e}")

# ==================== COMMAND HANDLERS ====================
@bot.on_message(filters.command("start") & filters.private)
async def start_cmd(client: Client, message: Message):
    if not is_admin(message.from_user.id):
        await message.reply("🚫 Unauthorized!")
        return

    buttons = InlineKeyboardMarkup([
        [InlineKeyboardButton("⚙️ Setup", callback_data="setup")],
        [InlineKeyboardButton("👑 Sudo", callback_data="sudo")],
        [InlineKeyboardButton("🚀 Start", callback_data="start_clone")]
    ])
    
    await message.reply(
        f"🤖 **Ultimate Cloner**\n\n"
        f"Owner: `{Config.ADMIN_ID}`\n"
        f"Status: `{'✅ Ready' if not Config.CLONING_ACTIVE else '🔄 Cloning'}`",
        reply_markup=buttons
    )

# ==================== CLONING SYSTEM ====================
async def clone_messages():
    """Core cloning function"""
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
@bot.on_callback_query()
async def callback_handler(client: Client, query: CallbackQuery):
    if query.data == "start_clone":
        if Config.CLONING_ACTIVE:
            await query.answer("Already cloning!", show_alert=True)
            return
            
        if not all([Config.TARGET_CHAT, Config.SOURCE_CHAT]):
            await query.answer("Set target/source first!", show_alert=True)
            return
            
        await query.answer("Starting clone job...")
        asyncio.create_task(clone_messages())

# ==================== MAIN ====================
async def main():
    await bot.start()
    print(f"""
╔══════════════════════╗
║   ULTIMATE CLONER    ║
╠══════════════════════╣
║ • Admin: {Config.ADMIN_ID}
║ • Sudo: {len(Config.SUDO_USERS)}
║ • Version: 2.0
╚══════════════════════╝
""")
    asyncio.create_task(health_ping())
    await idle()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nBot stopped manually")
    except Exception as e:
        print(f"Fatal error: {e}")
    finally:
        if bot.is_connected:
            asyncio.run(bot.stop())
