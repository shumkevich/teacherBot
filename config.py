import os
from dotenv import load_dotenv

load_dotenv()

# Telegram Bot Token
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")

# Google Sheets Settings
GOOGLE_SHEET_ID = os.getenv("GOOGLE_SHEET_ID")
SHEET_NAME = os.getenv("SHEET_NAME", "Sheet1")

# User Settings
PASSWORD = os.getenv("PASSWORD")

# Time for daily notifications
CHECK_TIME = "09:00"

# Admin Users (user_id from Telegram)
ALLOWED_USERS = [int(os.getenv("ADMIN_USER_ID"))]