import os
import sys
import time
import asyncio
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery

# ==================== BOT CONFIGURATION ====================
class BotConfig:
    ADMIN_ID = int(os.environ.get("ADMIN_ID", 0))
    SUDO_USERS = [int(x) for x in os.environ.get("SUDO_USERS", "").split(",") if x]
    TARGET_CHAT = ""
    SOURCE_CHAT = ""
    SKIP_MSG = 0
    FLOOD_DELAY = 32
    CLONING_ACTIVE = False

# ==================== HELPER FUNCTIONS ====================
def is_authorized(user_id: int) -> bool:
    return user_id == BotConfig.ADMIN_ID or user_id in BotConfig.SUDO_USERS

async def send_health_ping():
    while True:
        print("🫀 Health ping")
        await asyncio.sleep(300)

# ==================== BOT INITIALIZATION ====================
bot = Client(
    "UltimateCloner",
    api_id=int(os.environ["API_ID"]),
    api_hash=os.environ["API_HASH"],
    bot_token=os.environ["BOT_TOKEN"],
    workers=20
)

# ==================== COMMAND HANDLERS ====================
@bot.on_message(filters.command("start") & filters.private)
async def start_command(client: Client, message: Message):
    if not is_authorized(message.from_user.id):
        await message.reply("🚫 Unauthorized!")
        return

    buttons = InlineKeyboardMarkup([
        [InlineKeyboardButton("⚙️ Setup", callback_data="setup")],
        [InlineKeyboardButton("👑 Sudo Users", callback_data="sudo_menu")],
        [InlineKeyboardButton("🚀 Start Cloning", callback_data="start_clone")]
    ])
    
    await message.reply(
        f"👑 Owner: <code>{BotConfig.ADMIN_ID}</code>\n"
        f"⚡ Sudo Users: {len(BotConfig.SUDO_USERS)}\n\n"
        "Configure everything via buttons:",
        reply_markup=buttons
    )

# ==================== CLONING FUNCTION ====================
async def clone_messages(client: Client, callback: CallbackQuery):
    if not all([BotConfig.TARGET_CHAT, BotConfig.SOURCE_CHAT]):
        await callback.answer("❌ Set target/source first!", show_alert=True)
        return

    BotConfig.CLONING_ACTIVE = True
    status_msg = await callback.message.reply("🔄 Starting clone process...")

    try:
        async for msg in client.get_chat_history(BotConfig.SOURCE_CHAT):
            if not BotConfig.CLONING_ACTIVE:
                break

            await client.copy_message(
                chat_id=BotConfig.TARGET_CHAT,
                from_chat_id=BotConfig.SOURCE_CHAT,
                message_id=msg.id
            )
            await asyncio.sleep(BotConfig.FLOOD_DELAY)
            
    except Exception as e:
        await status_msg.edit(f"❌ Error: {str(e)}")
    finally:
        BotConfig.CLONING_ACTIVE = False
        await status_msg.edit("✅ Clone completed!")

# ==================== MAIN EXECUTION ====================
if __name__ == "__main__":
    async def main():
        await bot.start()
        asyncio.create_task(send_health_ping())
        print(f"""
⚡ Bot Started Successfully!
┌ Admin: {BotConfig.ADMIN_ID}
├ Sudo Users: {BotConfig.SUDO_USERS}
└ Ready to clone!
""")
        await idle()
        await bot.stop()

    from pyrogram.idle import idle
    asyncio.run(main())
