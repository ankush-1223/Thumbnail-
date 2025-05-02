import os
import sys
import time
import asyncio
from typing import List, Dict, Optional
from threading import Thread
from flask import Flask
from pyrogram import Client, filters, enums
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery

# =============== HEALTH CHECK SYSTEM ===============
class HealthCheck:
    @staticmethod
    def verify():
        if "--health-check" in sys.argv or "healthcheck" in sys.argv:
            print("HEALTH_CHECK_OK")
            sys.exit(0)

    @staticmethod
    async def keep_alive():
        while True:
            print("🫀 [Health] Alive at", time.strftime("%Y-%m-%d %H:%M:%S"))
            await asyncio.sleep(300)

# =============== BOT CONFIGURATION ===============
class BotConfig:
    API_ID = int(os.environ.get("API_ID", 0))
    API_HASH = os.environ.get("API_HASH", "")
    BOT_TOKEN = os.environ.get("BOT_TOKEN", "")
    ADMIN_ID = int(os.environ.get("ADMIN_ID", 0))
    
    SUDO_USERS: List[int] = []
    TARGET_CHAT: str = ""
    SOURCE_CHAT: str = ""
    SKIP_MSG: int = 0
    FLOOD_DELAY: int = 32
    CLONING_ACTIVE: bool = False
    STATUS_MESSAGE: Optional[Message] = None
    
    stats: Dict[str, int] = {
        'fetched': 0,
        'forwarded': 0,
        'skipped': 0,
        'errors': 0
    }

def is_authorized(user_id: int) -> bool:
    return user_id == BotConfig.ADMIN_ID or user_id in BotConfig.SUDO_USERS

# =============== BOT INSTANCE ===============
bot = Client(
    name="UltimateCloner",
    api_id=BotConfig.API_ID,
    api_hash=BotConfig.API_HASH,
    bot_token=BotConfig.BOT_TOKEN,
    workers=100,
    sleep_threshold=60
)

# =============== /start COMMAND ===============
@bot.on_message(filters.command("start") & filters.private)
async def start_command(client: Client, message: Message):
    if not is_authorized(message.from_user.id):
        await message.reply("🚫 Unauthorized access!")
        return

    buttons = InlineKeyboardMarkup([
        [InlineKeyboardButton("⚙️ Setup Bot", callback_data="bot_setup")],
        [
            InlineKeyboardButton("👑 Sudo Users", callback_data="sudo_menu"),
            InlineKeyboardButton("📊 Stats", callback_data="view_stats")
        ],
        [InlineKeyboardButton("🚀 Start Cloning", callback_data="start_cloning")]
    ])
    
    await message.reply(
        f"🤖 **Ultimate Cloner Bot**\n\n"
        f"▫️ **Owner:** `{BotConfig.ADMIN_ID}`\n"
        f"▫️ **Sudo Users:** `{len(BotConfig.SUDO_USERS)}`\n"
        f"▫️ **Status:** `{'Ready' if not BotConfig.CLONING_ACTIVE else 'Cloning...'}`\n\n"
        "Configure your cloning settings:",
        reply_markup=buttons
    )

# =============== CLONING FUNCTION ===============
async def update_status():
    while BotConfig.CLONING_ACTIVE:
        progress = (BotConfig.stats['forwarded'] / 
                   (BotConfig.stats['fetched'] - BotConfig.SKIP_MSG)) * 100 if BotConfig.stats['fetched'] > 0 else 0
        
        text = (
            "🔄 **Cloning Progress**\n\n"
            f"▫️ Fetched: `{BotConfig.stats['fetched']}`\n"
            f"▫️ Forwarded: `{BotConfig.stats['forwarded']}`\n"
            f"▫️ Skipped: `{BotConfig.stats['skipped']}`\n"
            f"▫️ Errors: `{BotConfig.stats['errors']}`\n"
            f"▫️ Progress: `{progress:.2f}%`\n\n"
            f"⏳ Next in `{BotConfig.FLOOD_DELAY}s`"
        )
        
        try:
            if BotConfig.STATUS_MESSAGE:
                await BotConfig.STATUS_MESSAGE.edit(text)
            await asyncio.sleep(5)
        except:
            pass

async def clone_messages(client: Client):
    BotConfig.CLONING_ACTIVE = True
    BotConfig.STATUS_MESSAGE = await client.send_message(
        BotConfig.ADMIN_ID,
        "🔄 Starting cloning process..."
    )
    
    asyncio.create_task(update_status())
    
    try:
        async for message in client.get_chat_history(BotConfig.SOURCE_CHAT):
            if not BotConfig.CLONING_ACTIVE:
                break
                
            BotConfig.stats['fetched'] += 1
            
            if BotConfig.stats['fetched'] <= BotConfig.SKIP_MSG:
                BotConfig.stats['skipped'] += 1
                continue
                
            try:
                await client.copy_message(
                    chat_id=BotConfig.TARGET_CHAT,
                    from_chat_id=BotConfig.SOURCE_CHAT,
                    message_id=message.id
                )
                BotConfig.stats['forwarded'] += 1
                await asyncio.sleep(BotConfig.FLOOD_DELAY)
            except Exception as e:
                BotConfig.stats['errors'] += 1
                print(f"Error cloning: {e}")
                
    finally:
        BotConfig.CLONING_ACTIVE = False
        await BotConfig.STATUS_MESSAGE.edit(
            f"✅ **Cloning Complete**\n\n"
            f"Total forwarded: `{BotConfig.stats['forwarded']}`\n"
            f"Total errors: `{BotConfig.stats['errors']}`"
        )

# =============== CALLBACK QUERIES ===============
@bot.on_callback_query()
async def handle_callbacks(client: Client, query: CallbackQuery):
    if query.data == "start_cloning":
        if BotConfig.CLONING_ACTIVE:
            await query.answer("⚠️ Cloning already in progress!", show_alert=True)
            return
            
        if not all([BotConfig.TARGET_CHAT, BotConfig.SOURCE_CHAT]):
            await query.answer("❌ Configure target/source first!", show_alert=True)
            return
            
        await query.answer("Starting clone job...")
        asyncio.create_task(clone_messages(client))
        
    elif query.data == "bot_setup":
        await query.answer("⚙️ Setup options not implemented yet!", show_alert=True)
        
    elif query.data == "sudo_menu":
        await query.answer("👑 Sudo management not implemented yet!", show_alert=True)

# =============== FLASK SERVER FOR KEYOB TCP CHECK ===============
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is alive!"

def run_web():
    app.run(host="0.0.0.0", port=8080)

# =============== START EVERYTHING ===============
if __name__ == "__main__":
    HealthCheck.verify()
    Thread(target=run_web).start()
    
    async def start_bot():
        await bot.start()
        asyncio.create_task(HealthCheck.keep_alive())
        print(f"""
███████╗ ██████╗ ████████╗
██╔════╝██╔═══██╗╚══██╔══╝
█████╗  ██║   ██║   ██║   
██╔══╝  ██║   ██║   ██║   
███████╗╚██████╔╝   ██║   
╚══════╝ ╚═════╝    ╚═╝   

✅ Bot started successfully!
▫️ Admin ID: {BotConfig.ADMIN_ID}
▫️ Ready to clone!
""")
        await idle()

    from pyrogram import idle  # ✅ Correct
    asyncio.run(start_bot())
