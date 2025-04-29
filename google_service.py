import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime, timedelta
import os

# Подключение к Google Sheets
SCOPE = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/spreadsheets",
         "https://www.googleapis.com/auth/drive.file", "https://www.googleapis.com/auth/drive"]

CREDS_FILE = "apigooglebotdasha.json"
SPREADSHEET_ID = "1NcoQVZwdK5u-GJk96H3rTgMElEtKJm2MUOlXhUOchKA"

credentials = ServiceAccountCredentials.from_json_keyfile_name(CREDS_FILE, SCOPE)
gc = gspread.authorize(credentials)
sheet = gc.open_by_key(SPREADSHEET_ID).sheet1


def get_active_tasks():
    data = sheet.get_all_records()
    active = []
    for idx, row in enumerate(data):
        if row['статус'].lower() not in ['выполнено', 'отменено']:
            row['id'] = idx + 2  # +2: первая строка — заголовок, индексация с 1
            active.append(row)
    return active


def update_task_status(row_index, new_status):
    sheet.update_cell(row_index, 3, new_status)  # Статус — 3-й столбец


def update_task_date(row_index, days):
    new_date = (datetime.now() + timedelta(days=days)).strftime("%Y-%m-%d")
    sheet.update_cell(row_index, 2, new_date)  # Дата — 2-й столбец
    sheet.update_cell(row_index, 3, "отложено")
