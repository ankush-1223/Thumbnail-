import os

class Config:
    # Required (will be set in Keyob's dashboard)
    API_ID = int(os.environ.get("API_ID"))  # Keyob variable
    API_HASH = os.environ.get("API_HASH")   # Keyob variable
    BOT_TOKEN = os.environ.get("BOT_TOKEN") # Keyob variable
    ADMIN_ID = int(os.environ.get("ADMIN_ID")) # Keyob variable
    
    # Optional (can be set via bot commands)
    SUDO_USERS = os.environ.get("SUDO_USERS", "").split(",") if os.environ.get("SUDO_USERS") else []
    FLOOD_DELAY = int(os.environ.get("FLOOD_DELAY", 32))
