import os, json, base64
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# Имя листа в вашей таблице
SHEET_NAME = "Лист1"

def authenticate_google_sheets():
    # читаем одну Base64-строку
    b64 = os.getenv("GOOGLE_CREDENTIALS_B64")
    if not b64:
        raise ValueError("GOOGLE_CREDENTIALS_B64 не установлена")

    # декодируем Base64 → получаем JSON bytes → превращаем в Python-строку и в dict
    data = base64.b64decode(b64)
    creds_dict = json.loads(data)

    scope = ['https://spreadsheets.google.com/feeds',
             'https://www.googleapis.com/auth/drive']
    creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
    return gspread.authorize(creds)

def get_tasks():
    sheet = authenticate_google_sheets().worksheet(SHEET_NAME)
    return sheet.get_all_records()

def update_task_status(task_name, new_status):
    sheet = authenticate_google_sheets().worksheet(SHEET_NAME)
    cell = sheet.find(task_name)
    if cell:
        sheet.update_cell(cell.row, 3, new_status)

def update_task_date(task_name, new_date):
    sheet = authenticate_google_sheets().worksheet(SHEET_NAME)
    cell = sheet.find(task_name)
    if cell:
        sheet.update_cell(cell.row, 2, new_date)
