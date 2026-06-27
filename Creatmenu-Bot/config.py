import os

# Main Bot Token
BOT_TOKEN = os.getenv(
    "BOT_TOKEN",
    "PASTE_YOUR_MAIN_BOT_TOKEN_HERE"
)

# Admin ID
ADMIN_ID = 7983838654

# Database
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "sqlite:///database.db"
)

# Share System
FREE_BOTS = 3
EXTRA_BOTS = 5
SHARE_REQUIRED = 10

# Force Join
FORCE_JOIN_CHANNEL = ""

# Bot Messages
BANNED_MESSAGE = (
    "🚫 System Banned\n\n"
    "Contact: @Scholes1"
)

UNKNOWN_MESSAGE = (
    "DON'T UNDERSTAND"
)
