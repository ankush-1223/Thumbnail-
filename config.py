from dotenv import load_dotenv
import os

load_dotenv()

class Config:
    API_ID = int(os.getenv("API_ID"))
    API_HASH = os.getenv("API_HASH")
    BOT_TOKEN = os.getenv("BOT_TOKEN")
    MAIN_CHANNEL = os.getenv("MAIN_CHANNEL", "")
    ADMIN_ID = os.getenv("ADMIN_ID")
