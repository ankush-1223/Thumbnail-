import os
import sys
import time
import asyncio
from typing import List, Dict, Optional
from pyrogram import Client, filters
from pyrogram.types import (
    Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
)

# ==================== HEALTH CHECK SYSTEM ====================
class HealthCheck:
    @staticmethod
    def verify():
        if "--health-check" in sys.argv or "healthcheck" in sys.argv:
            print("HEALTH_CHECK_OK")
            sys.exit(0)

    @staticmethod
    async def keep_alive():
        while True:
            print("🫀 [Health] Bot alive at", time.strftime("%Y-%m-%d %H:%M:%S"))
            await asyncio.sleep(300)

# ==================== BOT CONFIGURATION ====================
class Config:
    API_ID = int(os.environ.get("API_ID", 0))
    API_HASH = os.environ.get("API_HASH", "")
    BOT_TOKEN = os.environ.get("BOT_TOKEN", "")
    ADMIN_ID = int(os.environ.get("ADMIN_ID", 0))

    SUDO_USERS: List[int] = []
    TARGET_CHAT: str = ""
    SOURCE_CHAT: str = ""
    SKIP_MSG: int = 0
    FLOOD_DELAY: int = 5
    CLONING_ACTIVE: bool = False
    STATUS_MESSAGE: Optional[Message] = None

    stats: Dict[str, int] = {
        'fetched': 0,
        'forwarded': 0,
        'skipped': 0,
        'errors': 0
    }

# ==================== AUTH CHECK ====================
def is_admin(uid: int) -> bool:
    return uid == Config.ADMIN_ID or uid in Config.SUDO_USERS

# ==================== BOT INIT ====================
bot = Client(
    "UltimateCloner",
    api_id=Config.API_ID,
    api_hash=Config.API_HASH,
    bot_token=Config.BOT_TOKEN,
    workers=100,
    sleep_threshold=60
)

# ==================== COMMAND HANDLERS ====================
@bot.on_message(filters.command("start") & filters.private)
async def start(client: Client, message: Message):
    if not is_admin(message.from_user.id):
        return await message.reply("🚫 Access Denied")

    btns = InlineKeyboardMarkup([
        [InlineKeyboardButton("⚙️ Setup", callback_data="setup")],
        [
            InlineKeyboardButton("👑 Sudo", callback_data="sudo_menu"),
            InlineKeyboardButton("📊 Stats", callback_data="stats")
        ],
        [InlineKeyboardButton("🚀 Start Cloning", callback_data="start_clone")]
    ])

    await message.reply(
        f"🤖 **Ultimate Cloner Bot**\n\n"
        f"▫️ Owner: `{Config.ADMIN_ID}`\n"
        f"▫️ Sudo Users: `{len(Config.SUDO_USERS)}`\n"
        f"▫️ Cloning: `{'Active' if Config.CLONING_ACTIVE else 'Idle'}`\n\n"
        "Configure cloning settings below:",
        reply_markup=btns
    )

# ==================== CLONING SYSTEM ====================
async def update_status():
    while Config.CLONING_ACTIVE:
        total = Config.stats['fetched'] - Config.SKIP_MSG
        percent = (Config.stats['forwarded'] / total * 100) if total > 0 else 0

        txt = (
            "🔄 **Cloning Progress**\n\n"
            f"▫️ Fetched: `{Config.stats['fetched']}`\n"
            f"▫️ Forwarded: `{Config.stats['forwarded']}`\n"
            f"▫️ Skipped: `{Config.stats['skipped']}`\n"
            f"▫️ Errors: `{Config.stats['errors']}`\n"
            f"▫️ Progress: `{percent:.2f}%`\n"
        )
        try:
            if Config.STATUS_MESSAGE:
                await Config.STATUS_MESSAGE.edit(txt)
            await asyncio.sleep(5)
        except:
            pass

async def start_cloning(client: Client):
    Config.CLONING_ACTIVE = True
    Config.STATUS_MESSAGE = await client.send_message(Config.ADMIN_ID, "🔄 Cloning started...")
    asyncio.create_task(update_status())

    try:
        async for msg in client.get_chat_history(Config.SOURCE_CHAT):
            if not Config.CLONING_ACTIVE:
                break

            Config.stats['fetched'] += 1
            if Config.stats['fetched'] <= Config.SKIP_MSG:
                Config.stats['skipped'] += 1
                continue

            try:
                await client.copy_message(
                    chat_id=Config.TARGET_CHAT,
                    from_chat_id=Config.SOURCE_CHAT,
                    message_id=msg.id
                )
                Config.stats['forwarded'] += 1
                await asyncio.sleep(Config.FLOOD_DELAY)
            except Exception as e:
                Config.stats['errors'] += 1
                print(f"Error: {e}")

    finally:
        Config.CLONING_ACTIVE = False
        await Config.STATUS_MESSAGE.edit(
            f"✅ **Clone Finished**\n"
            f"Forwarded: `{Config.stats['forwarded']}`\n"
            f"Errors: `{Config.stats['errors']}`"
        )

# ==================== CALLBACK HANDLERS ====================
@bot.on_callback_query()
async def cb(client: Client, query: CallbackQuery):
    uid = query.from_user.id
    if not is_admin(uid):
        return await query.answer("🚫 Not authorized", show_alert=True)

    data = query.data
    if data == "start_clone":
        if Config.CLONING_ACTIVE:
            return await query.answer("⚠️ Already running!", show_alert=True)
        if not all([Config.SOURCE_CHAT, Config.TARGET_CHAT]):
            return await query.answer("❌ Source/Target not set!", show_alert=True)
        await query.answer("Starting cloning...")
        asyncio.create_task(start_cloning(client))

    elif data == "stats":
        total = Config.stats['fetched'] - Config.SKIP_MSG
        percent = (Config.stats['forwarded'] / total * 100) if total > 0 else 0
        await query.message.edit(
            f"📊 **Current Stats**\n\n"
            f"Fetched: `{Config.stats['fetched']}`\n"
            f"Forwarded: `{Config.stats['forwarded']}`\n"
            f"Skipped: `{Config.stats['skipped']}`\n"
            f"Errors: `{Config.stats['errors']}`\n"
            f"Progress: `{percent:.2f}%`"
        )

    elif data == "setup":
        await query.message.edit("⚙️ Bot setup not yet implemented.")

    elif data == "sudo_menu":
        await query.message.edit("👑 Sudo user management not yet implemented.")

# ==================== STARTUP ====================
@bot.on_startup()
async def on_startup(client: Client):
    HealthCheck.verify()
    asyncio.create_task(HealthCheck.keep_alive())
    print(f"✅ Bot started! Admin: {Config.ADMIN_ID}")

# ==================== MAIN ====================
if __name__ == "__main__":
    HealthCheck.verify()
    bot.run()
