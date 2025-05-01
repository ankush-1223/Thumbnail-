import os
import time
from pyrogram import Client, filters, enums
from pyrogram.types import (
    Message, InlineKeyboardMarkup,
    InlineKeyboardButton, CallbackQuery
)

# Initialize with Keyob environment variables
bot = Client(
    "UltimateCloner",
    api_id=int(os.environ["API_ID"]),
    api_hash=os.environ["API_HASH"],
    bot_token=os.environ["BOT_TOKEN"]
)

class BotConfig:
    ADMIN_ID = int(os.environ["ADMIN_ID"])
    SUDO_USERS = [int(x) for x in os.environ.get("SUDO_USERS", "").split(",") if x]
    TARGET_CHAT = ""
    SOURCE_CHAT = ""
    START_MSG_ID = 0
    SKIP_MSG = 0
    FLOOD_DELAY = int(os.environ.get("FLOOD_DELAY", 32))
    USE_THUMBNAIL = "remove"
    CLONING = False

# Helper Functions
def is_authorized(user_id: int) -> bool:
    return user_id == BotConfig.ADMIN_ID or user_id in BotConfig.SUDO_USERS

def generate_stats(fetched: int, forwarded: int, skipped: int) -> str:
    total = fetched - skipped
    percent = (forwarded / total * 100) if total > 0 else 0
    return (
        "📊 **Forward Status**\n\n"
        f"• Fetched: `{fetched}`\n"
        f"• Forwarded: `{forwarded}`\n"
        f"• Skipped: `{skipped}`\n"
        f"• Progress: `{percent:.1f}%`\n"
        f"• Next in: `{BotConfig.FLOOD_DELAY}s`"
    )

# Command Handlers
@bot.on_message(filters.command("start") & filters.private)
async def start(client: Client, message: Message):
    if not is_authorized(message.from_user.id):
        await message.reply("🚫 Unauthorized access!")
        return

    buttons = [
        [InlineKeyboardButton("⚙️ Setup", callback_data="setup")],
        [InlineKeyboardButton("👑 Sudo Users", callback_data="sudo_menu")],
        [InlineKeyboardButton("🚀 Start Cloning", callback_data="start_clone")]
    ]
    await message.reply(
        f"👑 **Owner**: `{BotConfig.ADMIN_ID}`\n"
        f"⚡ **Sudo Users**: `{len(BotConfig.SUDO_USERS)}`\n\n"
        "Configure everything via buttons:",
        reply_markup=InlineKeyboardMarkup(buttons)
    )

# Setup Menu
@bot.on_callback_query(filters.regex("^setup$"))
async def setup_menu(client: Client, query: CallbackQuery):
    buttons = [
        [InlineKeyboardButton("🎯 Set Target", callback_data="set_target")],
        [InlineKeyboardButton("🔗 Set Source", callback_data="set_source")],
        [InlineKeyboardButton("⏱ Set Delay", callback_data="set_delay")],
        [InlineKeyboardButton("🖼 Thumbnail", callback_data="set_thumb")],
        [InlineKeyboardButton("🔙 Back", callback_data="main_menu")]
    ]
    await query.edit_message_text(
        "⚙️ **Bot Configuration**\n\n"
        f"• Target: `{BotConfig.TARGET_CHAT or 'Not set'}`\n"
        f"• Source: `{BotConfig.SOURCE_CHAT or 'Not set'}`\n"
        f"• Delay: `{BotConfig.FLOOD_DELAY}s`\n"
        f"• Thumbnail: `{BotConfig.USE_THUMBNAIL}`",
        reply_markup=InlineKeyboardMarkup(buttons)
    )

# Sudo Management
@bot.on_callback_query(filters.regex("^sudo_menu$"))
async def sudo_menu(client: Client, query: CallbackQuery):
    if query.from_user.id != BotConfig.ADMIN_ID:
        await query.answer("👑 Owner-only feature!", show_alert=True)
        return

    buttons = [
        [InlineKeyboardButton("➕ Add Sudo", callback_data="add_sudo")],
        [InlineKeyboardButton("➖ Remove Sudo", callback_data="remove_sudo")],
        [InlineKeyboardButton("👥 List Sudo", callback_data="list_sudo")],
        [InlineKeyboardButton("🔙 Back", callback_data="main_menu")]
    ]
    await query.edit_message_text(
        f"👥 **Sudo Users**\n\nTotal: {len(BotConfig.SUDO_USERS)}\n"
        "Manage privileged users:",
        reply_markup=InlineKeyboardMarkup(buttons)
    )

# Clone Functionality
@bot.on_callback_query(filters.regex("^start_clone$"))
async def start_cloning(client: Client, query: CallbackQuery):
    if not BotConfig.TARGET_CHAT or not BotConfig.SOURCE_CHAT:
        await query.answer("❌ Set target/source first!", show_alert=True)
        return

    BotConfig.CLONING = True
    stats_msg = await query.message.reply("🔄 Starting clone process...")

    fetched = forwarded = 0
    async for msg in client.get_chat_history(BotConfig.SOURCE_CHAT):
        if not BotConfig.CLONING:
            break

        fetched += 1
        if fetched <= BotConfig.SKIP_MSG:
            continue

        try:
            await client.copy_message(
                chat_id=BotConfig.TARGET_CHAT,
                from_chat_id=BotConfig.SOURCE_CHAT,
                message_id=msg.id
            )
            forwarded += 1
        except Exception as e:
            print(f"Error forwarding: {e}")

        if fetched % 10 == 0:
            await stats_msg.edit(generate_stats(fetched, forwarded, BotConfig.SKIP_MSG))
            time.sleep(BotConfig.FLOOD_DELAY)

    BotConfig.CLONING = False
    await stats_msg.edit(
        f"✅ **Clone Completed**\n\n"
        f"{generate_stats(fetched, forwarded, BotConfig.SKIP_MSG)}\n\n"
        "Type /start to clone again."
    )

# Stop Command
@bot.on_message(filters.command("stop") & filters.private)
async def stop_cloning(client: Client, message: Message):
    if not is_authorized(message.from_user.id):
        return

    BotConfig.CLONING = False
    await message.reply("⏹ Clone process stopped!")

# Health Check for Keyob
if "--health-check" in os.sys.argv:
    print("OK")
    os.sys.exit(0)

if __name__ == "__main__":
    print("⚡ Bot started with config:")
    print(f"Admin: {BotConfig.ADMIN_ID}")
    print(f"Sudo Users: {BotConfig.SUDO_USERS}")
    bot.run()
