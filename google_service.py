import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime, timedelta
import os

# Подключение к Google Sheets
SCOPE = [
    "https://spreadsheets.google.com/feeds", 
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive.file", 
    "https://www.googleapis.com/auth/drive"
]

CREDS_FILE = os.getenv("GOOGLE_CREDS_FILE")
SPREADSHEET_ID = os.getenv("SPREADSHEET_ID")

credentials = ServiceAccountCredentials.from_json_keyfile_name(CREDS_FILE, SCOPE)
gc = gspread.authorize(credentials)
sheet = gc.open_by_key(SPREADSHEET_ID).sheet1

def get_active_tasks():
    try:
        data = sheet.get_all_records()
        active = []
        for idx, row in enumerate(data):
            if row['статус'].lower() not in ['выполнено', 'отменено']:
                row['id'] = idx + 2  # +2: первая строка — заголовок
                active.append(row)
        return active
    except Exception as e:
        print(f"Error retrieving tasks: {e}")
        return []

def update_task_status(row_index, new_status):
    try:
        sheet.update_cell(row_index, 3, new_status)  # Статус — 3-й столбец
    except Exception as e:
        print(f"Error updating status: {e}")

def update_task_date(row_index, days):
    try:
        new_date = (datetime.now() + timedelta(days=days)).strftime("%Y-%m-%d")
        sheet.update_cell(row_index, 2, new_date)  # Дата — 2-й столбец
        sheet.update_cell(row_index, 3, "отложено")  # Статус — отложено
    except Exception as e:
        print(f"Error updating date: {e}")